import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Colors, Typography, Spacing, BorderRadius } from '../theme';
import { api } from '../services/api';

export const StreakBanner: React.FC = () => {
  const [activity, setActivity] = useState<any>(null);

  useEffect(() => {
    api.getDailyActivity().then(setActivity).catch(console.error);
  }, []);

  if (!activity) return null;

  return (
    <View style={styles.container}>
      <View style={styles.row}>
        <View style={styles.stat}>
          <Text style={styles.number}>{activity.current_streak}</Text>
          <Text style={Typography.caption}>day streak 🔥</Text>
        </View>
        <View style={styles.stat}>
          <Text style={styles.number}>{activity.posts_remaining}</Text>
          <Text style={Typography.caption}>posts left today</Text>
        </View>
        <View style={styles.stat}>
          <Text style={styles.number}>{activity.replies_remaining}</Text>
          <Text style={Typography.caption}>replies left today</Text>
        </View>
      </View>
      {activity.streak_bonus_active && (
        <Text style={styles.bonus}>⚡ Streak bonus active — +20% clout on all posts!</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    marginHorizontal: Spacing.lg,
    marginBottom: Spacing.md,
    padding: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  row: { flexDirection: 'row', justifyContent: 'space-around' },
  stat: { alignItems: 'center' },
  number: { fontSize: 24, fontWeight: '800', color: Colors.accentPink },
  bonus: { color: Colors.accentPink, fontSize: 12, fontWeight: '600', textAlign: 'center', marginTop: Spacing.sm },
});
