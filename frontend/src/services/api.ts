const BASE_URL = 'http://localhost:8000';

let authToken: string | null = null;

const headers = () => ({
  'Content-Type': 'application/json',
  ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
});

async function request(method: string, path: string, body?: any) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: headers(),
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export const api = {
  setToken: (token: string) => { authToken = token; },

  // Auth
  register: (phone: string, displayName: string) =>
    request('POST', '/auth/register', { phone, display_name: displayName }),
  login: (phone: string) =>
    request('POST', '/auth/login', { phone }),

  // Feed
  getFeed: () => request('GET', '/posts/feed'),

  // Posts
  createPost: (data: { video_key: string; prompt_text: string; duration_seconds: number }) =>
    request('POST', '/posts/', data),
  getUploadUrl: () => request('POST', '/posts/upload-url'),

  // Replies
  createReply: (postId: string, data: { video_key: string; duration_seconds: number }) =>
    request('POST', `/posts/${postId}/replies`, data),
  getReplies: (postId: string) =>
    request('GET', `/posts/${postId}/replies`),

  // Engagement
  likePost: (postId: string) =>
    request('POST', `/engagement/like/${postId}`),
  likeReply: (replyId: string) =>
    request('POST', `/engagement/like-reply/${replyId}`),
  recordWatchTime: (postId: string, seconds: number) =>
    request('POST', `/engagement/watch`, { post_id: postId, seconds }),

  // Boosts
  purchaseBoost: (boostType: string, targetId: string) =>
    request('POST', '/boosts/purchase', { boost_type: boostType, target_id: targetId }),

  // Profile
  getProfile: () => request('GET', '/users/me'),
  updateProfile: (data: any) => request('PUT', '/users/me', data),

  // === NEW FEATURES ===

  // Daily Prompts
  getTodaysPrompts: () => request('GET', '/prompts/today'),
  getPromptHistory: (days: number = 7) => request('GET', `/prompts/history?days=${days}`),

  // Conversations (DMs)
  getConversations: () => request('GET', '/conversations/'),
  getMessages: (convoId: string) => request('GET', `/conversations/${convoId}/messages`),
  sendMessage: (convoId: string, body: string, videoKey?: string) =>
    request('POST', `/conversations/${convoId}/messages`, { body, video_key: videoKey }),

  // Notifications
  getNotifications: (limit: number = 50) => request('GET', `/notifications/?limit=${limit}`),
  markAllNotificationsRead: () => request('POST', '/notifications/read-all'),
  getUnreadCount: () => request('GET', '/notifications/unread-count'),

  // Verification
  getVerificationStatus: () => request('GET', '/verification/status'),
  // submitVerification uses FormData, handled separately in the screen

  // Activity / Streaks
  getDailyActivity: () => request('GET', '/activity/daily'),
};
