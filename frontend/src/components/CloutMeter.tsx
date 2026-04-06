import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import { Colors, Gradients, Typography, Spacing, BorderRadius } from '../theme';

interface Props {
  score: number; // 0-100
  tier: 'A' | 'B' | 'C';
  animated?: boolean;
}

export const CloutMeter: React.FC<Props> = ({ score, tier, animated = true }) => {
  const widthAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (animated) {
      Animated.spring(widthAnim, {
        toValue: score,
        friction: 8,
        tension: 40,
        useNativeDriver: false,
      }).start();
    } else {
      widthAnim.setValue(score);
    }
  }, [score]);

  const tierLabel = tier === 'A' ? 'ELITE' : tier === 'B' ? 'RISING' : 'STARTER';
  const gradient = tier === 'A' ? Gradients.gold : tier === 'B' ? Gradients.primary : Gradients.dark;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={Typography.caption}>CLOUT SCORE</Text>
        <Text style={[Typography.stat, { color: Colors[`tier${tier}`] }]}>{Math.round(score)}</Text>
      </View>
      <View style={styles.track}>
        <Animated.View style={{
          width: widthAnim.interpolate({
            inputRange: [0, 100],
            outputRange: ['0%', '100%'],
          }),
          height: '100%',
          borderRadius: BorderRadius.full,
          overflow: 'hidden',
        }}>
          <LinearGradient
            colors={gradient}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={{ flex: 1, borderRadius: BorderRadius.full }}
          />
        </Animated.View>
      </View>
      <Text style={[Typography.caption, { marginTop: Spacing.xs, color: Colors[`tier${tier}`] }]}>
        {tierLabel}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  track: {
    height: 6,
    backgroundColor: Colors.surfaceLight,
    borderRadius: BorderRadius.full,
    overflow: 'hidden',
  },
});
