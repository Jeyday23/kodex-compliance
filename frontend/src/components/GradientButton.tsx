import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import { Colors, Gradients, Typography, BorderRadius, Spacing } from '../theme';

interface Props {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'fire' | 'gold' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  style?: ViewStyle;
}

export const GradientButton: React.FC<Props> = ({
  title, onPress, variant = 'primary', size = 'md',
  loading, disabled, icon, style,
}) => {
  const gradientColors = variant === 'outline'
    ? [Colors.surface, Colors.surface]
    : Gradients[variant] || Gradients.primary;

  const height = size === 'sm' ? 40 : size === 'lg' ? 56 : 48;

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.85}
      style={style}
    >
      <LinearGradient
        colors={gradientColors}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
        style={[
          styles.button,
          { height },
          variant === 'outline' && styles.outline,
          disabled && styles.disabled,
        ]}
      >
        {loading ? (
          <ActivityIndicator color="#FFF" />
        ) : (
          <>
            {icon}
            <Text style={[
              Typography.button,
              icon ? { marginLeft: Spacing.sm } : null,
              variant === 'outline' && { color: Colors.accentPink },
            ]}>
              {title}
            </Text>
          </>
        )}
      </LinearGradient>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: BorderRadius.xl,
    paddingHorizontal: Spacing.lg,
  },
  outline: {
    borderWidth: 1.5,
    borderColor: Colors.accentPink,
  },
  disabled: {
    opacity: 0.5,
  },
});
