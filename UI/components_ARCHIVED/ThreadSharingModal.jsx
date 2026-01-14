/**
 * Thread Sharing Modal Component
 * 
 * Features:
 * - Share threads with users (direct share)
 * - Send email invitations
 * - Select role (viewer/editor/admin)
 * - List current collaborators
 * - Remove user access
 */

import React, { useState, useEffect } from 'react';

const ThreadSharingModal = ({ threadSlug, threadTitle, isOpen, onClose, currentUserId }) => {
    const [activeTab, setActiveTab] = useState('share'); // 'share' or 'collaborators'
    const [shareMethod, setShareMethod] = useState('direct'); // 'direct' or 'email'
    const [selectedUserId, setSelectedUserId] = useState('');
    const [email, setEmail] = useState('');
    const [role, setRole] = useState('viewer');
    const [collaborators, setCollaborators] = useState([]);
    const [availableUsers, setAvailableUsers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    // Load collaborators when modal opens
    useEffect(() => {
        if (isOpen && threadSlug) {
            loadCollaborators();
            if (shareMethod === 'direct') {
                loadAvailableUsers();
            }
        }
    }, [isOpen, threadSlug, shareMethod]);

    const loadCollaborators = async () => {
        try {
            const response = await fetch(`/api/threads/${threadSlug}/collaborators`, {
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                setCollaborators(data.collaborators || []);
            }
        } catch (err) {
            console.error('Failed to load collaborators:', err);
        }
    };

    const loadAvailableUsers = async () => {
        try {
            // Get all users from the system
            const response = await fetch('/api/auth/users', {
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                // Filter out current user and existing collaborators
                const collaboratorIds = collaborators.map(c => c.user_id);
                const filtered = data.users.filter(u =>
                    u.id !== currentUserId && !collaboratorIds.includes(u.id)
                );
                setAvailableUsers(filtered);
            }
        } catch (err) {
            console.error('Failed to load users:', err);
        }
    };

    const handleShare = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccess('');

        try {
            let response;

            if (shareMethod === 'direct') {
                if (!selectedUserId) {
                    setError('Please select a user');
                    setLoading(false);
                    return;
                }

                response = await fetch(`/api/threads/${threadSlug}/share`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({
                        shared_with_user_id: parseInt(selectedUserId),
                        role: role,
                        _user_id: currentUserId
                    })
                });
            } else {
                if (!email) {
                    setError('Please enter an email address');
                    setLoading(false);
                    return;
                }

                response = await fetch(`/api/threads/${threadSlug}/share-email`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({
                        email: email,
                        role: role,
                        _user_id: currentUserId
                    })
                });
            }

            const data = await response.json();

            if (response.ok && data.success) {
                setSuccess(
                    shareMethod === 'direct'
                        ? 'Thread shared successfully!'
                        : 'Invitation sent successfully!'
                );

                // Reset form
                setSelectedUserId('');
                setEmail('');
                setRole('viewer');

                // Reload collaborators
                setTimeout(() => {
                    loadCollaborators();
                    setSuccess('');
                }, 2000);
            } else {
                setError(data.error || 'Failed to share thread');
            }
        } catch (err) {
            setError('Network error. Please try again.');
            console.error('Share error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleRemoveAccess = async (userId) => {
        if (!confirm('Remove this user\'s access to the thread?')) {
            return;
        }

        setLoading(true);
        setError('');

        try {
            const response = await fetch(`/api/threads/${threadSlug}/share/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    _user_id: currentUserId
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                setSuccess('Access revoked successfully');
                loadCollaborators();
                setTimeout(() => setSuccess(''), 2000);
            } else {
                setError(data.error || 'Failed to revoke access');
            }
        } catch (err) {
            setError('Network error. Please try again.');
            console.error('Revoke error:', err);
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content thread-sharing-modal" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Share Thread</h2>
                    <button className="close-btn" onClick={onClose}>&times;</button>
                </div>

                <div className="modal-subtitle">
                    <strong>{threadTitle || threadSlug}</strong>
                </div>

                <div className="tabs">
                    <button
                        className={activeTab === 'share' ? 'tab active' : 'tab'}
                        onClick={() => setActiveTab('share')}
                    >
                        Share
                    </button>
                    <button
                        className={activeTab === 'collaborators' ? 'tab active' : 'tab'}
                        onClick={() => setActiveTab('collaborators')}
                    >
                        Collaborators ({collaborators.length})
                    </button>
                </div>

                {error && (
                    <div className="alert alert-error">
                        {error}
                    </div>
                )}

                {success && (
                    <div className="alert alert-success">
                        {success}
                    </div>
                )}

                {activeTab === 'share' && (
                    <form onSubmit={handleShare} className="share-form">
                        <div className="share-method-toggle">
                            <button
                                type="button"
                                className={shareMethod === 'direct' ? 'active' : ''}
                                onClick={() => setShareMethod('direct')}
                            >
                                Share with User
                            </button>
                            <button
                                type="button"
                                className={shareMethod === 'email' ? 'active' : ''}
                                onClick={() => setShareMethod('email')}
                            >
                                Send Invitation
                            </button>
                        </div>

                        {shareMethod === 'direct' ? (
                            <div className="form-group">
                                <label>Select User</label>
                                <select
                                    value={selectedUserId}
                                    onChange={e => setSelectedUserId(e.target.value)}
                                    required
                                >
                                    <option value="">Choose a user...</option>
                                    {availableUsers.map(user => (
                                        <option key={user.id} value={user.id}>
                                            {user.username || user.email}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        ) : (
                            <div className="form-group">
                                <label>Email Address</label>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={e => setEmail(e.target.value)}
                                    placeholder="user@example.com"
                                    required
                                />
                            </div>
                        )}

                        <div className="form-group">
                            <label>Role</label>
                            <select value={role} onChange={e => setRole(e.target.value)}>
                                <option value="viewer">Viewer (read-only)</option>
                                <option value="editor">Editor (read and write)</option>
                                <option value="admin">Admin (full control)</option>
                            </select>
                            <small className="form-help">
                                {role === 'viewer' && 'Can view thread but not edit'}
                                {role === 'editor' && 'Can view and add messages'}
                                {role === 'admin' && 'Can view, edit, and manage sharing'}
                            </small>
                        </div>

                        <button type="submit" className="btn-primary" disabled={loading}>
                            {loading ? 'Sharing...' : (shareMethod === 'direct' ? 'Share Thread' : 'Send Invitation')}
                        </button>
                    </form>
                )}

                {activeTab === 'collaborators' && (
                    <div className="collaborators-list">
                        {collaborators.length === 0 ? (
                            <p className="empty-state">No collaborators yet. Share this thread to collaborate!</p>
                        ) : (
                            <div className="collaborator-items">
                                {collaborators.map(collab => (
                                    <div key={collab.id} className="collaborator-item">
                                        <div className="collaborator-info">
                                            <div className="collaborator-name">
                                                {collab.username || collab.email || `User ${collab.user_id}`}
                                            </div>
                                            <div className="collaborator-role">
                                                <span className={`role-badge role-${collab.role}`}>
                                                    {collab.role}
                                                </span>
                                                <span className="collaborator-date">
                                                    Added {new Date(collab.added_at).toLocaleDateString()}
                                                </span>
                                            </div>
                                        </div>
                                        <button
                                            className="btn-remove"
                                            onClick={() => handleRemoveAccess(collab.user_id)}
                                            disabled={loading}
                                        >
                                            Remove
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>

            <style jsx>{`
                .modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.5);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 1000;
                }

                .modal-content {
                    background: white;
                    border-radius: 8px;
                    width: 90%;
                    max-width: 600px;
                    max-height: 80vh;
                    overflow-y: auto;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }

                .modal-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 20px;
                    border-bottom: 1px solid #e5e7eb;
                }

                .modal-header h2 {
                    margin: 0;
                    font-size: 1.5rem;
                }

                .close-btn {
                    background: none;
                    border: none;
                    font-size: 2rem;
                    cursor: pointer;
                    color: #6b7280;
                }

                .close-btn:hover {
                    color: #374151;
                }

                .modal-subtitle {
                    padding: 10px 20px;
                    background: #f9fafb;
                    color: #6b7280;
                    font-size: 0.9rem;
                }

                .tabs {
                    display: flex;
                    border-bottom: 1px solid #e5e7eb;
                    padding: 0 20px;
                }

                .tab {
                    padding: 12px 20px;
                    background: none;
                    border: none;
                    cursor: pointer;
                    font-size: 1rem;
                    color: #6b7280;
                    border-bottom: 2px solid transparent;
                }

                .tab.active {
                    color: #2563eb;
                    border-bottom-color: #2563eb;
                }

                .alert {
                    margin: 20px;
                    padding: 12px;
                    border-radius: 6px;
                }

                .alert-error {
                    background: #fee2e2;
                    color: #991b1b;
                }

                .alert-success {
                    background: #d1fae5;
                    color: #065f46;
                }

                .share-form {
                    padding: 20px;
                }

                .share-method-toggle {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 20px;
                }

                .share-method-toggle button {
                    flex: 1;
                    padding: 10px;
                    border: 1px solid #d1d5db;
                    background: white;
                    border-radius: 6px;
                    cursor: pointer;
                }

                .share-method-toggle button.active {
                    background: #2563eb;
                    color: white;
                    border-color: #2563eb;
                }

                .form-group {
                    margin-bottom: 20px;
                }

                .form-group label {
                    display: block;
                    margin-bottom: 8px;
                    font-weight: 500;
                    color: #374151;
                }

                .form-group input,
                .form-group select {
                    width: 100%;
                    padding: 10px;
                    border: 1px solid #d1d5db;
                    border-radius: 6px;
                    font-size: 1rem;
                }

                .form-help {
                    display: block;
                    margin-top: 5px;
                    font-size: 0.85rem;
                    color: #6b7280;
                }

                .btn-primary {
                    width: 100%;
                    padding: 12px;
                    background: #2563eb;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 1rem;
                    font-weight: 500;
                    cursor: pointer;
                }

                .btn-primary:hover {
                    background: #1d4ed8;
                }

                .btn-primary:disabled {
                    background: #9ca3af;
                    cursor: not-allowed;
                }

                .collaborators-list {
                    padding: 20px;
                }

                .empty-state {
                    text-align: center;
                    color: #6b7280;
                    padding: 40px 20px;
                }

                .collaborator-items {
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }

                .collaborator-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 15px;
                    border: 1px solid #e5e7eb;
                    border-radius: 6px;
                }

                .collaborator-info {
                    flex: 1;
                }

                .collaborator-name {
                    font-weight: 500;
                    color: #111827;
                    margin-bottom: 5px;
                }

                .collaborator-role {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }

                .role-badge {
                    display: inline-block;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 0.75rem;
                    font-weight: 500;
                    text-transform: uppercase;
                }

                .role-viewer {
                    background: #dbeafe;
                    color: #1e40af;
                }

                .role-editor {
                    background: #fef3c7;
                    color: #92400e;
                }

                .role-admin {
                    background: #fce7f3;
                    color: #9f1239;
                }

                .collaborator-date {
                    font-size: 0.85rem;
                    color: #6b7280;
                }

                .btn-remove {
                    padding: 8px 16px;
                    background: #fee2e2;
                    color: #991b1b;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 0.9rem;
                }

                .btn-remove:hover {
                    background: #fecaca;
                }

                .btn-remove:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }
            `}</style>
        </div>
    );
};

export default ThreadSharingModal;
