import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { Colors, BorderRadius, Spacing } from '../theme';

interface Props {
  children: React.ReactNode;
  style?: ViewStyle;
  glow?: boolean;
}

export const GlassCard: React.FC<Props> = ({ children, style, glow }) => (
  <View style={[
    styles.card,
    glow && styles.glow,
    style,
  ]}>
    {children}
  </View>
);

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.surfaceGlass,
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.06)',
    // Glassmorphism shadow
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  glow: {
    borderColor: 'rgba(255, 59, 122, 0.3)',
    shadowColor: '#FF3B7A',
    shadowOpacity: 0.2,
  },
});
