import React, { useState, useRef } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity,
  Dimensions, Animated,
} from 'react-native';
import Video from 'react-native-video';
import LinearGradient from 'react-native-linear-gradient';
import { Colors, Gradients, Typography, Spacing, BorderRadius } from '../theme';
import { TierBadge } from './TierBadge';
import { GlassCard } from './GlassCard';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');
const CARD_WIDTH = SCREEN_WIDTH - Spacing.lg * 2;
const CARD_HEIGHT = SCREEN_HEIGHT * 0.65;

interface Props {
  post: {
    id: string;
    author_name: string;
    author_tier: 'A' | 'B' | 'C';
    video_url: string;
    prompt_text: string;
    reply_count: number;
    like_count: number;
    view_count: number;
    is_boosted: boolean;
  };
  onReply: (postId: string) => void;
  onLike: (postId: string) => void;
  onBoost: (postId: string) => void;
}

export const VideoCard: React.FC<Props> = ({ post, onReply, onLike, onBoost }) => {
  const [paused, setPaused] = useState(false);
  const scaleAnim = useRef(new Animated.Value(1)).current;

  const handleLike = () => {
    // Heart burst animation
    Animated.sequence([
      Animated.spring(scaleAnim, { toValue: 1.3, friction: 3, useNativeDriver: true }),
      Animated.spring(scaleAnim, { toValue: 1, friction: 5, useNativeDriver: true }),
    ]).start();
    onLike(post.id);
  };

  return (
    <View style={[styles.card, post.is_boosted && styles.boostedCard]}>
      {/* Video Player */}
      <TouchableOpacity
        activeOpacity={1}
        onPress={() => setPaused(!paused)}
        style={styles.videoContainer}
      >
        <Video
          source={{ uri: post.video_url }}
          style={styles.video}
          resizeMode="cover"
          repeat
          paused={paused}
          muted={false}
        />

        {/* Gradient overlay at bottom */}
        <LinearGradient
          colors={['transparent', 'rgba(0,0,0,0.8)']}
          style={styles.gradient}
        />

        {/* Boosted indicator */}
        {post.is_boosted && (
          <LinearGradient
            colors={Gradients.fire}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={styles.boostedTag}
          >
            <Text style={styles.boostedText}>🔥 BOOSTED</Text>
          </LinearGradient>
        )}

        {/* Author info */}
        <View style={styles.authorRow}>
          <TierBadge tier={post.author_tier} />
          <Text style={[Typography.h3, { marginLeft: Spacing.sm }]}>{post.author_name}</Text>
        </View>

        {/* Prompt */}
        <View style={styles.promptContainer}>
          <Text style={styles.promptText}>"{post.prompt_text}"</Text>
        </View>

        {/* Stats bar */}
        <View style={styles.statsRow}>
          <View style={styles.stat}>
            <Text style={styles.statNumber}>{post.view_count}</Text>
            <Text style={styles.statLabel}>views</Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statNumber}>{post.reply_count}</Text>
            <Text style={styles.statLabel}>replies</Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statNumber}>{post.like_count}</Text>
            <Text style={styles.statLabel}>likes</Text>
          </View>
        </View>
      </TouchableOpacity>

      {/* Action buttons */}
      <View style={styles.actions}>
        <TouchableOpacity style={styles.actionBtn} onPress={() => onReply(post.id)}>
          <LinearGradient colors={Gradients.primary} style={styles.actionGradient}>
            <Text style={styles.actionIcon}>🎬</Text>
            <Text style={styles.actionLabel}>Reply</Text>
          </LinearGradient>
        </TouchableOpacity>

        <TouchableOpacity onPress={handleLike}>
          <Animated.View style={[styles.actionBtn, { transform: [{ scale: scaleAnim }] }]}>
            <View style={styles.actionOutline}>
              <Text style={styles.actionIcon}>❤️</Text>
            </View>
          </Animated.View>
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionBtn} onPress={() => onBoost(post.id)}>
          <LinearGradient colors={Gradients.gold} style={styles.actionGradient}>
            <Text style={styles.actionIcon}>⚡</Text>
            <Text style={styles.actionLabel}>Boost</Text>
          </LinearGradient>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    width: CARD_WIDTH,
    height: CARD_HEIGHT,
    borderRadius: BorderRadius.xl,
    overflow: 'hidden',
    backgroundColor: Colors.surface,
    marginBottom: Spacing.lg,
    // Shadow
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.4,
    shadowRadius: 20,
    elevation: 12,
  },
  boostedCard: {
    borderWidth: 2,
    borderColor: Colors.accentPink,
    shadowColor: Colors.accentPink,
    shadowOpacity: 0.3,
  },
  videoContainer: {
    flex: 1,
  },
  video: {
    ...StyleSheet.absoluteFillObject,
    borderRadius: BorderRadius.xl,
  },
  gradient: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: '50%',
  },
  boostedTag: {
    position: 'absolute',
    top: Spacing.md,
    right: Spacing.md,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.full,
  },
  boostedText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#FFF',
    letterSpacing: 1,
  },
  authorRow: {
    position: 'absolute',
    bottom: 100,
    left: Spacing.md,
    flexDirection: 'row',
    alignItems: 'center',
  },
  promptContainer: {
    position: 'absolute',
    bottom: 60,
    left: Spacing.md,
    right: Spacing.md,
  },
  promptText: {
    ...Typography.h3,
    fontSize: 16,
    fontStyle: 'italic',
    color: 'rgba(255,255,255,0.9)',
  },
  statsRow: {
    position: 'absolute',
    bottom: Spacing.md,
    left: Spacing.md,
    flexDirection: 'row',
    gap: Spacing.lg,
  },
  stat: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 16,
    fontWeight: '800',
    color: '#FFF',
  },
  statLabel: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.6)',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: Spacing.md,
    gap: Spacing.md,
    backgroundColor: Colors.surface,
  },
  actionBtn: {
    borderRadius: BorderRadius.xl,
    overflow: 'hidden',
  },
  actionGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.sm + 2,
    borderRadius: BorderRadius.xl,
    gap: Spacing.xs,
  },
  actionOutline: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm + 2,
    borderRadius: BorderRadius.xl,
    borderWidth: 1.5,
    borderColor: 'rgba(255,255,255,0.15)',
  },
  actionIcon: {
    fontSize: 18,
  },
  actionLabel: {
    ...Typography.button,
    fontSize: 14,
  },
});
