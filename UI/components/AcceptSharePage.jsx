/**
 * Accept Thread Share Page
 * 
 * Handles thread share invitation acceptance via token URL:
 * /accept-thread-share/<token>
 * 
 * Features:
 * - Display thread details
 * - Show who shared the thread
 * - Display role being granted
 * - Accept/Decline buttons
 * - Handle expired/invalid tokens
 * - Redirect to thread on success
 */

import React, { useState, useEffect } from 'react';

const AcceptSharePage = ({ token, currentUserId, onAccept, onDecline }) => {
    const [loading, setLoading] = useState(true);
    const [shareData, setShareData] = useState(null);
    const [error, setError] = useState('');
    const [accepting, setAccepting] = useState(false);

    useEffect(() => {
        if (token) {
            loadShareDetails();
        }
    }, [token]);

    const loadShareDetails = async () => {
        try {
            // Get share invitation details
            const response = await fetch(`/api/thread-shares/details/${token}`, {
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                setShareData(data);
            } else {
                const data = await response.json();
                setError(data.error || 'Invalid or expired invitation');
            }
        } catch (err) {
            setError('Failed to load invitation details');
            console.error('Load error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleAccept = async () => {
        setAccepting(true);
        setError('');

        try {
            const response = await fetch(`/api/thread-shares/accept/${token}`, {
                method: 'POST',
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
                // Notify parent component
                if (onAccept) {
                    onAccept(data);
                }

                // Redirect to thread
                window.location.href = `/thread/${data.thread_slug}`;
            } else {
                setError(data.error || 'Failed to accept invitation');
            }
        } catch (err) {
            setError('Network error. Please try again.');
            console.error('Accept error:', err);
        } finally {
            setAccepting(false);
        }
    };

    const handleDecline = () => {
        if (onDecline) {
            onDecline();
        }

        // Redirect to home or dashboard
        window.location.href = '/';
    };

    if (loading) {
        return (
            <div className="accept-share-page">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Loading invitation...</p>
                </div>

                <style jsx>{`
                    .accept-share-page {
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        background: #f9fafb;
                    }

                    .loading-container {
                        text-align: center;
                    }

                    .spinner {
                        width: 40px;
                        height: 40px;
                        border: 4px solid #e5e7eb;
                        border-top-color: #2563eb;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                        margin: 0 auto 20px;
                    }

                    @keyframes spin {
                        to { transform: rotate(360deg); }
                    }
                `}</style>
            </div>
        );
    }

    if (error) {
        return (
            <div className="accept-share-page">
                <div className="error-container">
                    <div className="error-icon">⚠️</div>
                    <h2>Invalid Invitation</h2>
                    <p>{error}</p>
                    <button onClick={handleDecline} className="btn-secondary">
                        Go to Home
                    </button>
                </div>

                <style jsx>{`
                    .accept-share-page {
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        background: #f9fafb;
                    }

                    .error-container {
                        background: white;
                        border-radius: 12px;
                        padding: 40px;
                        max-width: 500px;
                        text-align: center;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    }

                    .error-icon {
                        font-size: 4rem;
                        margin-bottom: 20px;
                    }

                    .error-container h2 {
                        color: #991b1b;
                        margin-bottom: 10px;
                    }

                    .error-container p {
                        color: #6b7280;
                        margin-bottom: 30px;
                    }

                    .btn-secondary {
                        padding: 12px 24px;
                        background: #6b7280;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 1rem;
                        cursor: pointer;
                    }

                    .btn-secondary:hover {
                        background: #4b5563;
                    }
                `}</style>
            </div>
        );
    }

    return (
        <div className="accept-share-page">
            <div className="invitation-card">
                <div className="invitation-header">
                    <div className="icon">🔗</div>
                    <h1>You've been invited!</h1>
                </div>

                <div className="invitation-body">
                    <div className="info-section">
                        <div className="info-label">Thread</div>
                        <div className="info-value thread-title">
                            {shareData?.thread_title || shareData?.thread_slug}
                        </div>
                    </div>

                    <div className="info-section">
                        <div className="info-label">Shared by</div>
                        <div className="info-value">
                            {shareData?.shared_by_username || shareData?.shared_by_email || 'A user'}
                        </div>
                    </div>

                    <div className="info-section">
                        <div className="info-label">Your role</div>
                        <div className="info-value">
                            <span className={`role-badge role-${shareData?.role}`}>
                                {shareData?.role}
                            </span>
                            <span className="role-description">
                                {shareData?.role === 'viewer' && ' - You can view this thread'}
                                {shareData?.role === 'editor' && ' - You can view and edit this thread'}
                                {shareData?.role === 'admin' && ' - You have full control over this thread'}
                            </span>
                        </div>
                    </div>

                    {shareData?.expires_at && (
                        <div className="info-section">
                            <div className="info-label">Invitation expires</div>
                            <div className="info-value expiry-date">
                                {new Date(shareData.expires_at).toLocaleDateString('en-US', {
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric',
                                    hour: '2-digit',
                                    minute: '2-digit'
                                })}
                            </div>
                        </div>
                    )}
                </div>

                <div className="invitation-actions">
                    <button
                        onClick={handleAccept}
                        className="btn-accept"
                        disabled={accepting}
                    >
                        {accepting ? 'Accepting...' : 'Accept Invitation'}
                    </button>
                    <button
                        onClick={handleDecline}
                        className="btn-decline"
                        disabled={accepting}
                    >
                        Decline
                    </button>
                </div>
            </div>

            <style jsx>{`
                .accept-share-page {
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px;
                }

                .invitation-card {
                    background: white;
                    border-radius: 16px;
                    max-width: 600px;
                    width: 100%;
                    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
                                0 10px 10px -5px rgba(0, 0, 0, 0.04);
                    overflow: hidden;
                }

                .invitation-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }

                .invitation-header .icon {
                    font-size: 4rem;
                    margin-bottom: 15px;
                }

                .invitation-header h1 {
                    margin: 0;
                    font-size: 2rem;
                    font-weight: 600;
                }

                .invitation-body {
                    padding: 30px;
                }

                .info-section {
                    margin-bottom: 25px;
                }

                .info-section:last-child {
                    margin-bottom: 0;
                }

                .info-label {
                    font-size: 0.85rem;
                    font-weight: 500;
                    color: #6b7280;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    margin-bottom: 8px;
                }

                .info-value {
                    font-size: 1.1rem;
                    color: #111827;
                }

                .thread-title {
                    font-weight: 600;
                    font-size: 1.3rem;
                    color: #2563eb;
                }

                .role-badge {
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 0.85rem;
                    font-weight: 600;
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

                .role-description {
                    display: block;
                    font-size: 0.9rem;
                    color: #6b7280;
                    margin-top: 5px;
                }

                .expiry-date {
                    color: #6b7280;
                    font-size: 0.95rem;
                }

                .invitation-actions {
                    padding: 30px;
                    background: #f9fafb;
                    display: flex;
                    gap: 15px;
                }

                .btn-accept,
                .btn-decline {
                    flex: 1;
                    padding: 14px 24px;
                    border: none;
                    border-radius: 8px;
                    font-size: 1rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                }

                .btn-accept {
                    background: #2563eb;
                    color: white;
                }

                .btn-accept:hover:not(:disabled) {
                    background: #1d4ed8;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 6px rgba(37, 99, 235, 0.3);
                }

                .btn-accept:disabled {
                    background: #9ca3af;
                    cursor: not-allowed;
                }

                .btn-decline {
                    background: white;
                    color: #6b7280;
                    border: 2px solid #d1d5db;
                }

                .btn-decline:hover:not(:disabled) {
                    background: #f9fafb;
                    border-color: #9ca3af;
                }

                .btn-decline:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }

                @media (max-width: 640px) {
                    .invitation-header {
                        padding: 30px 20px;
                    }

                    .invitation-header h1 {
                        font-size: 1.5rem;
                    }

                    .invitation-body,
                    .invitation-actions {
                        padding: 20px;
                    }

                    .invitation-actions {
                        flex-direction: column;
                    }
                }
            `}</style>
        </div>
    );
};

export default AcceptSharePage;
