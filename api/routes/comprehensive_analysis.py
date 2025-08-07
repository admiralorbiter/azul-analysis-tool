"""
Comprehensive Analysis API Routes

This module provides REST API endpoints for accessing comprehensive analysis data
from the integrated exhaustive analysis system.
"""

from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
import os
import sys
import subprocess
import time

from core.azul_database import AzulDatabase, MoveQualityAnalysis, ComprehensiveMoveAnalysis, ExhaustiveAnalysisSession
from core.azul_model import AzulState

# Create blueprint
comprehensive_analysis_bp = Blueprint('comprehensive_analysis', __name__)

# Initialize database
db = AzulDatabase()


_runtime_sessions: Dict[str, Dict[str, Any]] = {}

@comprehensive_analysis_bp.route('/exhaustive-analysis/<position_fen>', methods=['GET'])
def get_exhaustive_analysis(position_fen: str):
    """
    Get comprehensive analysis for a specific position.
    
    Args:
        position_fen: FEN string of the position
        
    Returns:
        Comprehensive analysis results including move quality, engine consensus, etc.
    """
    try:
        # Get position ID
        position_id = db.get_position_id(position_fen)
        if not position_id:
            return jsonify({
                "success": False,
                "error": "Position not found in database"
            }), 404
        
        # Get the most recent move quality analysis for this position
        with db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM move_quality_analyses 
                WHERE position_id = ? 
                ORDER BY created_at DESC LIMIT 1
            """, (position_id,))
            
            row = cursor.fetchone()
            if not row:
                return jsonify({
                    "success": False,
                    "error": "No analysis found for this position"
                }), 404
            
            # Get comprehensive move analyses
            move_analyses = db.get_comprehensive_move_analyses(row['id'])
            
            # Format response
            analysis_data = {
                "position_fen": position_fen,
                "game_phase": row['game_phase'],
                "total_moves_analyzed": row['total_moves_analyzed'],
                "quality_distribution": json.loads(row['quality_distribution']),
                "average_quality_score": row['average_quality_score'],
                "best_move_score": row['best_move_score'],
                "worst_move_score": row['worst_move_score'],
                "engine_consensus": json.loads(row['engine_consensus']),
                "disagreement_level": row['disagreement_level'],
                "position_complexity": row['position_complexity'],
                "strategic_themes": json.loads(row['strategic_themes']),
                "tactical_opportunities": json.loads(row['tactical_opportunities']),
                "analysis_time": row['analysis_time'],
                "created_at": row['created_at'],
                "moves": []
            }
            
            # Add move analyses
            for move_analysis in move_analyses:
                analysis_data["moves"].append({
                    "move_data": move_analysis.move_data,
                    "alpha_beta_score": move_analysis.alpha_beta_score,
                    "mcts_score": move_analysis.mcts_score,
                    "neural_score": move_analysis.neural_score,
                    "pattern_score": move_analysis.pattern_score,
                    "overall_quality_score": move_analysis.overall_quality_score,
                    "quality_tier": move_analysis.quality_tier,
                    "confidence_score": move_analysis.confidence_score,
                    "strategic_value": move_analysis.strategic_value,
                    "tactical_value": move_analysis.tactical_value,
                    "risk_assessment": move_analysis.risk_assessment,
                    "opportunity_value": move_analysis.opportunity_value,
                    "blocking_score": move_analysis.blocking_score,
                    "scoring_score": move_analysis.scoring_score,
                    "floor_line_score": move_analysis.floor_line_score,
                    "timing_score": move_analysis.timing_score,
                    "engines_used": move_analysis.engines_used,
                    "explanation": move_analysis.explanation,
                    "analysis_time": move_analysis.analysis_time
                })
            
            return jsonify({
                "success": True,
                "analysis": analysis_data
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get analysis: {str(e)}"
        }), 500


@comprehensive_analysis_bp.route('/exhaustive-sessions', methods=['GET'])
def get_exhaustive_sessions():
    """
    Get all exhaustive analysis sessions.
    
    Query parameters:
        status: Filter by status ('running', 'completed', 'failed', 'stopped')
        limit: Maximum number of sessions to return (default: 50)
        
    Returns:
        List of exhaustive analysis sessions
    """
    try:
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        
        sessions = db.get_all_exhaustive_sessions(status=status, limit=limit)
        
        session_data = []
        for session in sessions:
            session_data.append({
                "session_id": session.session_id,
                "mode": session.mode,
                "positions_analyzed": session.positions_analyzed,
                "total_moves_analyzed": session.total_moves_analyzed,
                "total_analysis_time": session.total_analysis_time,
                "successful_analyses": session.successful_analyses,
                "failed_analyses": session.failed_analyses,
                "engine_stats": session.engine_stats,
                "status": session.status,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "completed_at": session.completed_at.isoformat() if session.completed_at else None
            })
        
        return jsonify({
            "success": True,
            "sessions": session_data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get sessions: {str(e)}"
        }), 500


@comprehensive_analysis_bp.route('/exhaustive-analysis/start', methods=['POST'])
def start_exhaustive_analysis():
    """
    Start an exhaustive analysis run in the background.

    Request JSON:
    {
      "mode": "quick|standard|deep|exhaustive",
      "positions": 100,
      "maxWorkers": 8,
      "sessionId": "optional"
    }
    """
    try:
        data = request.get_json() or {}
        mode = (data.get('mode') or 'standard').lower()
        positions = int(data.get('positions') or data.get('num_positions') or 100)
        max_workers = data.get('maxWorkers')
        session_id = data.get('sessionId') or f"session_{int(time.time())}"

        if mode not in {"quick", "standard", "deep", "exhaustive"}:
            return jsonify({
                "success": False,
                "error": f"Invalid mode: {mode}"
            }), 400

        # Resolve script path relative to repository root
        routes_dir = os.path.dirname(__file__)
        repo_root = os.path.normpath(os.path.join(routes_dir, '..', '..'))
        script_path = os.path.normpath(os.path.join(
            repo_root, 'move_quality_analysis', 'scripts', 'robust_exhaustive_analyzer.py'
        ))
        if not os.path.exists(script_path):
            return jsonify({
                "success": False,
                "error": f"Analyzer script not found at {script_path}"
            }), 500

        cmd = [sys.executable, script_path, '--mode', mode, '--positions', str(positions), '--session-id', session_id]
        if max_workers is not None:
            cmd.extend(['--workers', str(max_workers)])

        # Launch background process (detached, no inherited pipes)
        # Route output to per-session log for debugging/visibility
        logs_dir = os.path.join(repo_root, 'logs')
        try:
            os.makedirs(logs_dir, exist_ok=True)
        except Exception:
            pass
        log_path = os.path.join(logs_dir, f'exhaustive_{session_id}.log')
        stdout_target = open(log_path, 'a', buffering=1, encoding='utf-8', errors='ignore')
        stderr_target = subprocess.STDOUT
        popen_kwargs = {
            'cwd': repo_root,
            'stdout': stdout_target,
            'stderr': stderr_target,
            'close_fds': True,
        }
        # Detach process group in a cross-platform manner
        if os.name == 'nt':
            try:
                CREATE_NEW_PROCESS_GROUP = 0x00000200
                DETACHED_PROCESS = 0x00000008
                popen_kwargs['creationflags'] = CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS
            except Exception:
                pass
        else:
            popen_kwargs['start_new_session'] = True

        proc = subprocess.Popen(cmd, **popen_kwargs)

        _runtime_sessions[session_id] = {
            'status': 'running',
            'mode': mode,
            'planned_positions': positions,
            'start_time': time.time(),
            'pid': proc.pid
        }

        return jsonify({
            'success': True,
            'message': 'Analysis started',
            'session_id': session_id,
            'pid': proc.pid,
            'log_file': os.path.relpath(log_path, repo_root)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to start analysis: {str(e)}'
        }), 500


@comprehensive_analysis_bp.route('/exhaustive-analysis/progress/<session_id>', methods=['GET'])
def get_exhaustive_progress(session_id: str):
    try:
        runtime = _runtime_sessions.get(session_id, {})

        with db.get_connection() as conn:
            # Analyses written so far
            cursor = conn.execute(
                "SELECT COUNT(*) as cnt FROM move_quality_analyses WHERE session_id = ?",
                (session_id,)
            )
            analyzed = cursor.fetchone()['cnt']

            # Session row if present
            cursor = conn.execute(
                "SELECT status, positions_analyzed, total_analysis_time FROM exhaustive_analysis_sessions WHERE session_id = ?",
                (session_id,)
            )
            session_row = cursor.fetchone()

            # If no session row yet but we have some analyses, create/update a lightweight session row
            if not session_row and analyzed > 0:
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO exhaustive_analysis_sessions (session_id, mode, positions_analyzed, total_moves_analyzed, total_analysis_time, successful_analyses, failed_analyses, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                        (session_id, runtime.get('mode', 'unknown'), analyzed, 0, 0.0, analyzed, 0, 'running')
                    )
                    conn.commit()
                except Exception:
                    pass

        planned = int(runtime.get('planned_positions') or 0)
        percent = (analyzed / planned * 100.0) if planned > 0 else None

        status = runtime.get('status', 'running')
        # Prefer DB session status if available
        if session_row and session_row['status']:
            status = session_row['status']
        # If planned known and reached, mark completed
        if planned > 0 and analyzed >= planned and status != 'completed':
            status = 'completed'
            runtime['status'] = status
        
        # Fallback: if we've been polling for too long without progress, mark as completed
        start_time = runtime.get('start_time')
        if start_time and (time.time() - start_time) > 300:  # 5 minutes timeout
            status = 'completed'
            runtime['status'] = status

        start_time = runtime.get('start_time')
        elapsed = time.time() - start_time if start_time else None

        response_data = {
            'success': True,
            'session_id': session_id,
            'status': status,
            'positions_analyzed': analyzed,
            'planned_positions': planned,
            'progress_percent': round(percent, 1) if percent is not None else None,
            'elapsed_seconds': round(elapsed, 1) if elapsed is not None else None
        }
        
        # Add debug info for troubleshooting
        if current_app.debug:
            response_data['debug'] = {
                'session_row_exists': session_row is not None,
                'session_status': session_row['status'] if session_row else None,
                'runtime_status': runtime.get('status'),
                'start_time': start_time
            }
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get progress: {str(e)}'}), 500


@comprehensive_analysis_bp.route('/exhaustive-analysis/stop/<session_id>', methods=['POST'])
def stop_exhaustive_session(session_id: str):
    try:
        runtime = _runtime_sessions.get(session_id)
        if not runtime or not runtime.get('pid'):
            return jsonify({'success': False, 'error': 'Session not running'}), 404

        pid = runtime['pid']
        try:
            if os.name == 'nt':
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(pid)])
            else:
                os.kill(pid, 15)
            runtime['status'] = 'stopped'
        except Exception as te:
            return jsonify({'success': False, 'error': f'Failed to stop process: {te}'}), 500

        return jsonify({'success': True, 'session_id': session_id, 'status': 'stopped'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@comprehensive_analysis_bp.route('/exhaustive-analysis/results/<session_id>', methods=['GET'])
def get_exhaustive_results(session_id: str):
    return get_exhaustive_session(session_id)


@comprehensive_analysis_bp.route('/exhaustive-analysis/sessions', methods=['GET'])
def exhaustive_sessions_alias():
    return get_exhaustive_sessions()


@comprehensive_analysis_bp.route('/exhaustive-analysis/stats/<session_id>', methods=['GET'])
def get_session_stats(session_id: str):
    try:
        with db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) as cnt, SUM(total_moves_analyzed) as total_moves, AVG(average_quality_score) as avg_q "
                "FROM move_quality_analyses WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            analyzed = row['cnt'] or 0
            total_moves = row['total_moves'] or 0
            avg_q = row['avg_q'] or 0.0

        runtime = _runtime_sessions.get(session_id, {})
        planned = int(runtime.get('planned_positions') or 0)

        return jsonify({
            'success': True,
            'session_id': session_id,
            'positions_analyzed': analyzed,
            'planned_positions': planned,
            'total_moves_analyzed': int(total_moves),
            'average_quality_score': round(float(avg_q), 2)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@comprehensive_analysis_bp.route('/exhaustive-analysis/sessions/<session_id>', methods=['DELETE'])
def delete_exhaustive_session(session_id: str):
    try:
        runtime = _runtime_sessions.get(session_id)
        if runtime and runtime.get('pid'):
            try:
                if os.name == 'nt':
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(runtime['pid'])])
                else:
                    os.kill(runtime['pid'], 15)
                runtime['status'] = 'stopped'
            except Exception:
                pass

        with db.get_connection() as conn:
            conn.execute(
                "DELETE FROM comprehensive_move_analyses WHERE position_analysis_id IN ("
                " SELECT id FROM move_quality_analyses WHERE session_id = ?"
                ")",
                (session_id,)
            )
            conn.execute("DELETE FROM move_quality_analyses WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM exhaustive_analysis_sessions WHERE session_id = ?", (session_id,))
            conn.commit()

        return jsonify({'success': True, 'session_id': session_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@comprehensive_analysis_bp.route('/exhaustive-analysis/export/<session_id>', methods=['GET'])
def export_exhaustive_session(session_id: str):
    try:
        resp = get_exhaustive_session(session_id)
        return resp
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@comprehensive_analysis_bp.route('/exhaustive-analysis/status', methods=['GET'])
def exhaustive_system_status():
    try:
        running = [sid for sid, r in _runtime_sessions.items() if r.get('status') == 'running']
        return jsonify({
            'success': True,
            'status': 'operational',
            'running_sessions': running,
            'total_runtime_sessions': len(_runtime_sessions)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@comprehensive_analysis_bp.route('/exhaustive-session/<session_id>', methods=['GET'])
def get_exhaustive_session(session_id: str):
    """
    Get details of a specific exhaustive analysis session.
    
    Args:
        session_id: Session ID to retrieve
        
    Returns:
        Session details and analysis results
    """
    try:
        session = db.get_exhaustive_analysis_session(session_id)
        if not session:
            return jsonify({
                "success": False,
                "error": "Session not found"
            }), 404
        
        # Get analyses for this session
        with db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT mqa.*, p.fen_string FROM move_quality_analyses mqa
                JOIN positions p ON mqa.position_id = p.id
                WHERE mqa.session_id = ?
                ORDER BY mqa.created_at DESC
            """, (session_id,))
            
            analyses = []
            for row in cursor.fetchall():
                analyses.append({
                    "position_fen": row['fen_string'],
                    "game_phase": row['game_phase'],
                    "total_moves_analyzed": row['total_moves_analyzed'],
                    "quality_distribution": json.loads(row['quality_distribution']),
                    "average_quality_score": row['average_quality_score'],
                    "best_move_score": row['best_move_score'],
                    "worst_move_score": row['worst_move_score'],
                    "engine_consensus": json.loads(row['engine_consensus']),
                    "disagreement_level": row['disagreement_level'],
                    "position_complexity": row['position_complexity'],
                    "strategic_themes": json.loads(row['strategic_themes']),
                    "tactical_opportunities": json.loads(row['tactical_opportunities']),
                    "analysis_time": row['analysis_time'],
                    "created_at": row['created_at']
                })
        
        session_data = {
            "session_id": session.session_id,
            "mode": session.mode,
            "positions_analyzed": session.positions_analyzed,
            "total_moves_analyzed": session.total_moves_analyzed,
            "total_analysis_time": session.total_analysis_time,
            "successful_analyses": session.successful_analyses,
            "failed_analyses": session.failed_analyses,
            "engine_stats": session.engine_stats,
            "status": session.status,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "analyses": analyses
        }
        
        return jsonify({
            "success": True,
            "session": session_data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get session: {str(e)}"
        }), 500


@comprehensive_analysis_bp.route('/best-analyses', methods=['GET'])
def get_best_analyses():
    """
    Get the best move quality analyses (highest average scores).
    
    Query parameters:
        limit: Maximum number of analyses to return (default: 10)
        
    Returns:
        List of best analyses
    """
    try:
        limit = int(request.args.get('limit', 10))
        
        analyses = db.get_best_move_quality_analyses(limit=limit)
        
        analysis_data = []
        for analysis in analyses:
            analysis_data.append({
                "position_id": analysis.position_id,
                "session_id": analysis.session_id,
                "game_phase": analysis.game_phase,
                "total_moves_analyzed": analysis.total_moves_analyzed,
                "quality_distribution": analysis.quality_distribution,
                "average_quality_score": analysis.average_quality_score,
                "best_move_score": analysis.best_move_score,
                "worst_move_score": analysis.worst_move_score,
                "engine_consensus": analysis.engine_consensus,
                "disagreement_level": analysis.disagreement_level,
                "position_complexity": analysis.position_complexity,
                "strategic_themes": analysis.strategic_themes,
                "tactical_opportunities": analysis.tactical_opportunities,
                "analysis_time": analysis.analysis_time,
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None
            })
        
        return jsonify({
            "success": True,
            "analyses": analysis_data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get best analyses: {str(e)}"
        }), 500


@comprehensive_analysis_bp.route('/analysis-stats', methods=['GET'])
def get_analysis_stats():
    """
    Get comprehensive analysis statistics.
    
    Returns:
        Statistics about the exhaustive analysis system
    """
    try:
        with db.get_connection() as conn:
            # Get total counts
            cursor = conn.execute("SELECT COUNT(*) as count FROM move_quality_analyses")
            total_analyses = cursor.fetchone()['count']
            
            cursor = conn.execute("SELECT COUNT(*) as count FROM comprehensive_move_analyses")
            total_moves = cursor.fetchone()['count']
            
            cursor = conn.execute("SELECT COUNT(*) as count FROM exhaustive_analysis_sessions")
            total_sessions = cursor.fetchone()['count']
            
            # Get average scores
            cursor = conn.execute("SELECT AVG(average_quality_score) as avg_score FROM move_quality_analyses")
            avg_score = cursor.fetchone()['avg_score'] or 0.0
            
            # Get quality distribution
            cursor = conn.execute("""
                SELECT quality_distribution, COUNT(*) as count 
                FROM move_quality_analyses 
                GROUP BY quality_distribution
            """)
            
            quality_distributions = {}
            for row in cursor.fetchall():
                distribution = json.loads(row['quality_distribution'])
                count = row['count']
                for tier, count_in_dist in distribution.items():
                    if tier not in quality_distributions:
                        quality_distributions[tier] = 0
                    quality_distributions[tier] += count_in_dist * count
            
            # Get engine consensus stats
            cursor = conn.execute("""
                SELECT engine_consensus, COUNT(*) as count 
                FROM move_quality_analyses 
                WHERE engine_consensus IS NOT NULL
            """)
            
            engine_stats = {}
            for row in cursor.fetchall():
                consensus = json.loads(row['engine_consensus'])
                count = row['count']
                for engine, score in consensus.items():
                    if engine not in engine_stats:
                        engine_stats[engine] = {"total_score": 0, "count": 0}
                    engine_stats[engine]["total_score"] += score * count
                    engine_stats[engine]["count"] += count
            
            # Calculate averages
            for engine in engine_stats:
                if engine_stats[engine]["count"] > 0:
                    engine_stats[engine]["average_score"] = engine_stats[engine]["total_score"] / engine_stats[engine]["count"]
                else:
                    engine_stats[engine]["average_score"] = 0.0
        
        stats = {
            "total_analyses": total_analyses,
            "total_moves_analyzed": total_moves,
            "total_sessions": total_sessions,
            "average_quality_score": round(avg_score, 2),
            "quality_distribution": quality_distributions,
            "engine_statistics": engine_stats
        }
        
        return jsonify({
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get statistics: {str(e)}"
        }), 500


@comprehensive_analysis_bp.route('/search-positions', methods=['POST'])
def search_positions():
    """
    Search for positions with specific criteria.
    
    Request body:
    {
        "min_quality_score": 70.0,
        "game_phase": "mid",
        "min_moves_analyzed": 50,
        "max_disagreement": 0.5,
        "limit": 10
    }
    
    Returns:
        List of positions matching the criteria
    """
    try:
        data = request.get_json() or {}
        
        min_quality_score = data.get('min_quality_score', 0.0)
        game_phase = data.get('game_phase')
        min_moves_analyzed = data.get('min_moves_analyzed', 0)
        max_disagreement = data.get('max_disagreement', 1.0)
        limit = data.get('limit', 10)
        
        # Build query
        query = """
            SELECT mqa.*, p.fen_string FROM move_quality_analyses mqa
            JOIN positions p ON mqa.position_id = p.id
            WHERE mqa.average_quality_score >= ?
            AND mqa.total_moves_analyzed >= ?
            AND mqa.disagreement_level <= ?
        """
        params = [min_quality_score, min_moves_analyzed, max_disagreement]
        
        if game_phase:
            query += " AND mqa.game_phase = ?"
            params.append(game_phase)
        
        query += " ORDER BY mqa.average_quality_score DESC LIMIT ?"
        params.append(limit)
        
        with db.get_connection() as conn:
            cursor = conn.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "position_fen": row['fen_string'],
                    "game_phase": row['game_phase'],
                    "total_moves_analyzed": row['total_moves_analyzed'],
                    "quality_distribution": json.loads(row['quality_distribution']),
                    "average_quality_score": row['average_quality_score'],
                    "best_move_score": row['best_move_score'],
                    "worst_move_score": row['worst_move_score'],
                    "engine_consensus": json.loads(row['engine_consensus']),
                    "disagreement_level": row['disagreement_level'],
                    "position_complexity": row['position_complexity'],
                    "strategic_themes": json.loads(row['strategic_themes']),
                    "tactical_opportunities": json.loads(row['tactical_opportunities']),
                    "analysis_time": row['analysis_time'],
                    "created_at": row['created_at']
                })
        
        return jsonify({
            "success": True,
            "positions": results,
            "count": len(results)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to search positions: {str(e)}"
        }), 500 