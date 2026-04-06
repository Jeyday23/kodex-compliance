import React from 'react';
import {
  View, Text, StyleSheet, Modal, TouchableOpacity,
  Dimensions,
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import { Colors, Gradients, Typography, Spacing, BorderRadius } from '../theme';
import { GlassCard } from './GlassCard';
import { GradientButton } from './GradientButton';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface BoostOption {
  type: string;
  label: string;
  description: string;
  price: string;
  emoji: string;
  gradient: string[];
}

const BOOST_OPTIONS: BoostOption[] = [
  {
    type: 'reply_boost',
    label: 'Boost Reply',
    description: 'Push your reply to the top slots',
    price: '€2.99',
    emoji: '🚀',
    gradient: Gradients.primary,
  },
  {
    type: 'post_boost',
    label: 'Boost Post',
    description: 'Get seen by higher-tier users',
    price: '€9.99',
    emoji: '🔥',
    gradient: Gradients.fire,
  },
  {
    type: 'skip_the_line',
    label: 'Skip the Line',
    description: 'Appear in Tier A top responses',
    price: '€5.99',
    emoji: '⚡',
    gradient: Gradients.gold,
  },
  {
    type: 'resurface',
    label: 'Resurface',
    description: 'Re-appear after being seen',
    price: '€1.99',
    emoji: '👀',
    gradient: ['#10B981', '#059669'],
  },
];

interface Props {
  visible: boolean;
  onClose: () => void;
  onSelect: (boostType: string) => void;
  targetId: string;
}

export const BoostModal: React.FC<Props> = ({ visible, onClose, onSelect }) => (
  <Modal visible={visible} transparent animationType="slide">
    <View style={styles.overlay}>
      <View style={styles.sheet}>
        {/* Handle bar */}
        <View style={styles.handle} />

        <Text style={[Typography.h2, { textAlign: 'center', marginBottom: Spacing.xs }]}>
          ⚡ Power Up
        </Text>
        <Text style={[Typography.body, { textAlign: 'center', marginBottom: Spacing.lg }]}>
          Stand out from the crowd
        </Text>

        {BOOST_OPTIONS.map((opt) => (
          <TouchableOpacity
            key={opt.type}
            activeOpacity={0.85}
            onPress={() => onSelect(opt.type)}
            style={{ marginBottom: Spacing.md }}
          >
            <GlassCard glow>
              <View style={styles.optionRow}>
                <LinearGradient
                  colors={opt.gradient}
                  style={styles.optionIcon}
                >
                  <Text style={{ fontSize: 22 }}>{opt.emoji}</Text>
                </LinearGradient>
                <View style={styles.optionText}>
                  <Text style={Typography.h3}>{opt.label}</Text>
                  <Text style={Typography.body}>{opt.description}</Text>
                </View>
                <View style={styles.priceTag}>
                  <Text style={styles.priceText}>{opt.price}</Text>
                </View>
              </View>
            </GlassCard>
          </TouchableOpacity>
        ))}

        <GradientButton
          title="Cancel"
          variant="outline"
          onPress={onClose}
          style={{ marginTop: Spacing.sm }}
        />
      </View>
    </View>
  </Modal>
);

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: Colors.overlayDark,
    justifyContent: 'flex-end',
  },
  sheet: {
    backgroundColor: Colors.surface,
    borderTopLeftRadius: BorderRadius.xl,
    borderTopRightRadius: BorderRadius.xl,
    padding: Spacing.lg,
    paddingBottom: Spacing.xxl,
  },
  handle: {
    width: 40,
    height: 4,
    backgroundColor: Colors.textMuted,
    borderRadius: 2,
    alignSelf: 'center',
    marginBottom: Spacing.lg,
  },
  optionRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  optionIcon: {
    width: 48,
    height: 48,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  optionText: {
    flex: 1,
    marginLeft: Spacing.md,
  },
  priceTag: {
    backgroundColor: 'rgba(255, 59, 122, 0.15)',
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.full,
  },
  priceText: {
    ...Typography.button,
    fontSize: 14,
    color: Colors.accentPink,
  },
});
