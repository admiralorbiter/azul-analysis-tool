// ConfigurationModal Component
// Extracted from main.js Phase 4C

function ConfigurationModal({ config, onSave, onCancel, loading }) {
    const [formData, setFormData] = React.useState({
        name: config?.name || '',
        model_size: config?.model_size || 'small',
        device: config?.device || 'cpu',
        epochs: config?.epochs || 10,
        samples: config?.samples || 1000,
        batch_size: config?.batch_size || 32,
        learning_rate: config?.learning_rate || 0.001,
        is_default: config?.is_default || false
    });

    React.useEffect(() => {
        if (config) {
            setFormData({
                name: config.name || '',
                model_size: config.model_size || 'small',
                device: config.device || 'cpu',
                epochs: config.epochs || 10,
                samples: config.samples || 1000,
                batch_size: config.batch_size || 32,
                learning_rate: config.learning_rate || 0.001,
                is_default: config.is_default || false
            });
        }
    }, [config]);

    const handleSubmit = (e) => {
        e.preventDefault();
        onSave(formData);
    };

    return React.createElement('div', { className: 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50' },
        React.createElement('div', { className: 'relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white' },
            React.createElement('div', { className: 'mt-3' },
                React.createElement('div', { className: 'flex justify-between items-center mb-4' },
                    React.createElement('h3', { className: 'text-lg font-semibold text-gray-900' }, 
                        config ? 'Edit Configuration' : 'Add Configuration'
                    ),
                    React.createElement('button', {
                        onClick: onCancel,
                        className: 'text-gray-400 hover:text-gray-600'
                    }, '✕')
                ),
                React.createElement('form', { onSubmit: handleSubmit, className: 'space-y-4' },
                    React.createElement('div', { className: 'grid grid-cols-1 md:grid-cols-2 gap-4' },
                        React.createElement('div', { className: 'space-y-2' },
                            React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Name'),
                            React.createElement('input', {
                                type: 'text',
                                value: formData.name,
                                onChange: (e) => setFormData({...formData, name: e.target.value}),
                                className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                                required: true
                            })
                        ),
                        React.createElement('div', { className: 'space-y-2' },
                            React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Model Size'),
                            React.createElement('select', {
                                value: formData.model_size,
                                onChange: (e) => setFormData({...formData, model_size: e.target.value}),
                                className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                            },
                                React.createElement('option', { value: 'small' }, 'Small (Fast)'),
                                React.createElement('option', { value: 'medium' }, 'Medium (Balanced)'),
                                React.createElement('option', { value: 'large' }, 'Large (Accurate)')
                            )
                        ),
                        React.createElement('div', { className: 'space-y-2' },
                            React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Device'),
                            React.createElement('select', {
                                value: formData.device,
                                onChange: (e) => setFormData({...formData, device: e.target.value}),
                                className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                            },
                                React.createElement('option', { value: 'cpu' }, 'CPU'),
                                React.createElement('option', { value: 'gpu' }, 'GPU (if available)')
                            )
                        ),
                        React.createElement('div', { className: 'space-y-2' },
                            React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Epochs'),
                            React.createElement('input', {
                                type: 'number',
                                value: formData.epochs,
                                onChange: (e) => setFormData({...formData, epochs: parseInt(e.target.value)}),
                                min: 1,
                                max: 100,
                                className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                            })
                        ),
                        React.createElement('div', { className: 'space-y-2' },
                            React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Samples'),
                            React.createElement('input', {
                                type: 'number',
                                value: formData.samples,
                                onChange: (e) => setFormData({...formData, samples: parseInt(e.target.value)}),
                                min: 100,
                                max: 10000,
                                className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                            })
                        ),
                        React.createElement('div', { className: 'space-y-2' },
                            React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Batch Size'),
                            React.createElement('input', {
                                type: 'number',
                                value: formData.batch_size,
                                onChange: (e) => setFormData({...formData, batch_size: parseInt(e.target.value)}),
                                min: 1,
                                max: 128,
                                className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                            })
                        ),
                        React.createElement('div', { className: 'space-y-2' },
                            React.createElement('label', { className: 'block text-sm font-medium text-gray-700' }, 'Learning Rate'),
                            React.createElement('input', {
                                type: 'number',
                                value: formData.learning_rate,
                                onChange: (e) => setFormData({...formData, learning_rate: parseFloat(e.target.value)}),
                                step: 0.0001,
                                min: 0.0001,
                                max: 0.1,
                                className: 'w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent'
                            })
                        )
                    ),
                    React.createElement('div', { className: 'flex items-center space-x-2' },
                        React.createElement('input', {
                            type: 'checkbox',
                            id: 'is_default',
                            checked: formData.is_default,
                            onChange: (e) => setFormData({...formData, is_default: e.target.checked}),
                            className: 'rounded border-gray-300 text-purple-600 focus:ring-purple-500'
                        }),
                        React.createElement('label', { htmlFor: 'is_default', className: 'text-sm font-medium text-gray-700' }, 'Set as default configuration')
                    ),
                    React.createElement('div', { className: 'flex justify-end space-x-3 pt-4' },
                        React.createElement('button', {
                            type: 'button',
                            onClick: onCancel,
                            className: 'px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300'
                        }, 'Cancel'),
                        React.createElement('button', {
                            type: 'submit',
                            disabled: loading,
                            className: 'px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50'
                        }, loading ? 'Saving...' : 'Save Configuration')
                    )
                )
            )
        )
    );
} 