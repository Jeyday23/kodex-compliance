import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  Dimensions, StatusBar,
} from 'react-native';
import Video from 'react-native-video';
import LinearGradient from 'react-native-linear-gradient';
import { Colors, Gradients, Typography, Spacing, BorderRadius } from '../theme';
import { GlassCard, TierBadge, GradientButton } from '../components';
import { api } from '../services/api';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

export const RepliesScreen: React.FC<{ route: any; navigation: any }> = ({ route, navigation }) => {
  const { postId } = route.params;
  const [replies, setReplies] = useState<any[]>([]);
  const [activeReply, setActiveReply] = useState<string | null>(null);

  useEffect(() => {
    api.getReplies(postId).then(setReplies).catch(console.error);
  }, [postId]);

  const handleLike = async (replyId: string) => {
    try {
      await api.likeReply(postId, replyId);
      setReplies(prev => prev.map(r =>
        r.id === replyId ? { ...r, is_liked_by_poster: true, like_count: r.like_count + 1 } : r
      ));
    } catch {}
  };

  const renderReply = ({ item, index }: { item: any; index: number }) => (
    <GlassCard
      glow={item.is_boosted}
      style={[styles.replyCard, index === 0 && styles.topReply]}
    >
      {/* Rank badge */}
      <View style={styles.rankBadge}>
        <Text style={styles.rankText}>#{index + 1}</Text>
      </View>

      {/* Boosted tag */}
      {item.is_boosted && (
        <LinearGradient colors={Gradients.fire} style={styles.boostedPill}>
          <Text style={styles.boostedLabel}>⚡ BOOSTED</Text>
        </LinearGradient>
      )}

      {/* Video thumbnail / player */}
      <TouchableOpacity
        onPress={() => setActiveReply(activeReply === item.id ? null : item.id)}
        style={styles.videoThumb}
      >
        {activeReply === item.id ? (
          <Video
            source={{ uri: item.video_url }}
            style={styles.replyVideo}
            resizeMode="cover"
            repeat
          />
        ) : (
          <LinearGradient colors={Gradients.dark} style={styles.replyVideo}>
            <Text style={{ fontSize: 32 }}>▶️</Text>
          </LinearGradient>
        )}
      </TouchableOpacity>

      {/* Author + stats */}
      <View style={styles.replyInfo}>
        <View style={styles.replyAuthor}>
          <Text style={Typography.h3}>{item.author_name}</Text>
          {item.is_liked_by_poster && (
            <Text style={styles.matchBadge}>💘 MATCHED</Text>
          )}
        </View>

        <View style={styles.replyActions}>
          <TouchableOpacity
            onPress={() => handleLike(item.id)}
            style={[styles.likeBtn, item.is_liked_by_poster && styles.likeBtnActive]}
          >
            <Text style={{ fontSize: 20 }}>{item.is_liked_by_poster ? '💖' : '🤍'}</Text>
          </TouchableOpacity>
          <Text style={Typography.caption}>{item.like_count} likes</Text>
        </View>
      </View>
    </GlassCard>
  );

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" />

      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backBtn}>← Back</Text>
        </TouchableOpacity>
        <Text style={Typography.h3}>Replies</Text>
        <Text style={Typography.caption}>{replies.length} responses</Text>
      </View>

      <FlatList
        data={replies}
        keyExtractor={(item) => item.id}
        renderItem={renderReply}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={{ fontSize: 48, marginBottom: Spacing.md }}>🦗</Text>
            <Text style={Typography.h3}>No replies yet</Text>
            <Text style={Typography.body}>Be the first to respond!</Text>
          </View>
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 60,
    paddingHorizontal: Spacing.lg,
    paddingBottom: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
  },
  backBtn: {
    color: Colors.accentPink,
    fontSize: 16,
    fontWeight: '600',
  },
  list: {
    padding: Spacing.lg,
    paddingBottom: 100,
  },
  replyCard: {
    marginBottom: Spacing.md,
    overflow: 'hidden',
  },
  topReply: {
    borderColor: 'rgba(255,215,0,0.3)',
    borderWidth: 1,
  },
  rankBadge: {
    position: 'absolute',
    top: Spacing.sm,
    left: Spacing.sm,
    backgroundColor: 'rgba(0,0,0,0.6)',
    paddingHorizontal: Spacing.sm,
    paddingVertical: 2,
    borderRadius: BorderRadius.sm,
    zIndex: 5,
  },
  rankText: {
    color: '#FFF',
    fontWeight: '800',
    fontSize: 12,
  },
  boostedPill: {
    position: 'absolute',
    top: Spacing.sm,
    right: Spacing.sm,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 2,
    borderRadius: BorderRadius.full,
    zIndex: 5,
  },
  boostedLabel: {
    color: '#FFF',
    fontWeight: '800',
    fontSize: 10,
    letterSpacing: 0.5,
  },
  videoThumb: {
    height: 200,
    borderRadius: BorderRadius.md,
    overflow: 'hidden',
    marginBottom: Spacing.md,
  },
  replyVideo: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: BorderRadius.md,
  },
  replyInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  replyAuthor: {
    flex: 1,
  },
  matchBadge: {
    color: Colors.accentPink,
    fontSize: 11,
    fontWeight: '800',
    marginTop: 2,
  },
  replyActions: {
    alignItems: 'center',
  },
  likeBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: Colors.surfaceLight,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 4,
  },
  likeBtnActive: {
    backgroundColor: 'rgba(255,59,122,0.15)',
  },
  empty: {
    alignItems: 'center',
    paddingTop: 100,
  },
});
