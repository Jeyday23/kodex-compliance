import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity } from 'react-native';
import { Colors, Typography, Spacing } from '../theme';
import { GlassCard } from '../components';
import { api } from '../services/api';

const ICONS: Record<string, string> = {
  new_reply: '🎬',
  reply_liked: '💘',
  post_liked: '❤️',
  match_created: '🔥',
  clout_spike: '📈',
  daily_prompt: '🎯',
  boost_expired: '⏰',
  streak_reminder: '🔥',
};

export const NotificationsScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [notifications, setNotifications] = useState<any[]>([]);

  useEffect(() => {
    loadNotifications();
    api.markAllNotificationsRead();
  }, []);

  const loadNotifications = async () => {
    try {
      const data = await api.getNotifications();
      setNotifications(data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={[Typography.h1, { padding: Spacing.lg, paddingTop: 60 }]}>
        Notifications 🔔
      </Text>
      <FlatList
        data={notifications}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <GlassCard style={[styles.notifCard, !item.is_read && styles.unread]}>
            <Text style={{ fontSize: 28 }}>{ICONS[item.type] || '📌'}</Text>
            <View style={{ flex: 1, marginLeft: Spacing.md }}>
              <Text style={Typography.h3}>{item.title}</Text>
              <Text style={[Typography.caption, { marginTop: 2 }]}>{item.body}</Text>
              <Text style={[Typography.caption, { marginTop: 4, fontSize: 10 }]}>
                {new Date(item.created_at).toLocaleDateString()}
              </Text>
            </View>
          </GlassCard>
        )}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={{ fontSize: 48 }}>🔕</Text>
            <Text style={[Typography.body, { textAlign: 'center', marginTop: Spacing.md }]}>
              Nothing yet — post a video{'\n'}and watch the love roll in
            </Text>
          </View>
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  notifCard: { flexDirection: 'row', alignItems: 'center', marginHorizontal: Spacing.lg, marginBottom: Spacing.sm, padding: Spacing.md },
  unread: { borderLeftWidth: 3, borderLeftColor: Colors.accentPink },
  empty: { alignItems: 'center', paddingTop: 120 },
});
