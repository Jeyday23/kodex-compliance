import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import { Colors, Gradients, BorderRadius, Typography } from '../theme';

interface Props {
  tier: 'A' | 'B' | 'C';
  size?: 'sm' | 'md';
}

const tierConfig = {
  A: { label: '🔥', gradient: Gradients.gold, glow: Colors.tierA },
  B: { label: '⚡', gradient: Gradients.primary, glow: Colors.tierB },
  C: { label: '💫', gradient: Gradients.dark, glow: Colors.tierC },
};

export const TierBadge: React.FC<Props> = ({ tier, size = 'sm' }) => {
  const config = tierConfig[tier];
  const dim = size === 'sm' ? 28 : 36;

  return (
    <LinearGradient
      colors={config.gradient}
      style={[
        styles.badge,
        { width: dim, height: dim, borderRadius: dim / 2 },
        { shadowColor: config.glow },
      ]}
    >
      <Text style={styles.emoji}>{config.label}</Text>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  badge: {
    alignItems: 'center',
    justifyContent: 'center',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.6,
    shadowRadius: 8,
    elevation: 6,
  },
  emoji: {
    fontSize: 14,
  },
});
