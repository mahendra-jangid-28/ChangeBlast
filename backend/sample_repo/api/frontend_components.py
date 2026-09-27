"""
Frontend React components that reference user IDs.
These are flagged when User.id type changes from Integer to UUID.
"""
# Simulating React component logic as Python comments/strings for search purposes

COMPONENTS = {
    "UserCard": """
// UserCard.jsx
import React from 'react';
export function UserCard({ user }) {
  // user.id is rendered as a number badge
  return (
    <div className="user-card">
      <span className="user-id">#{user.id}</span>
      <span>{user.full_name}</span>
    </div>
  );
}
""",
    "OrderHistory": """
// OrderHistory.jsx
import React from 'react';
export function OrderHistory({ userId }) {
  // userId is expected to be an integer for URL construction
  const url = `/api/users/${userId}/orders`;
  const [orders, setOrders] = React.useState([]);
  React.useEffect(() => {
    fetch(url).then(r => r.json()).then(setOrders);
  }, [userId]);
  return <div>{orders.map(o => <div key={o.id}>{o.status}</div>)}</div>;
}
""",
    "UserProfileLink": """
// UserProfileLink.jsx
export const buildProfileUrl = (userId) => `/profile/${userId}`;
// userId assumed integer — URL would look like /profile/42
// After UUID: /profile/550e8400-e29b-41d4-a716-446655440000
""",
}
