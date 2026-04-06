import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View, Text, StyleSheet, FlatList, StatusBar,
  RefreshControl, Dimensions, Animated,
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import { Colors, Gradients, Typography, Spacing } from '../theme';
import { VideoCard, BoostModal } from '../components';
import { api } from '../services/api';

const { height: SCREEN_HEIGHT } = Dimensions.get('window');

export const FeedScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [posts, setPosts] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [boostTarget, setBoostTarget] = useState<string | null>(null);
  const scrollY = useRef(new Animated.Value(0)).current;

  const loadFeed = useCallback(async () => {
    try {
      const data = await api.getFeed();
      setPosts(data);
    } catch (err) {
      console.error('Feed load error:', err);
    }
  }, []);

  useEffect(() => { loadFeed(); }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadFeed();
    setRefreshing(false);
  };

  const handleReply = (postId: string) => {
    navigation.navigate('Record', { postId, mode: 'reply' });
  };

  const handleLike = async (postId: string) => {
    try {
      await api.likePost(postId);
      setPosts(prev => prev.map(p =>
        p.id === postId ? { ...p, like_count: p.like_count + 1 } : p
      ));
    } catch {}
  };

  const handleBoostSelect = async (boostType: string) => {
    if (!boostTarget) return;
    try {
      const result = await api.purchaseBoost(boostType, boostTarget);
      // Open Stripe payment sheet with result.client_secret
      setBoostTarget(null);
    } catch (err) {
      console.error('Boost error:', err);
    }
  };

  // Header opacity animation
  const headerOpacity = scrollY.interpolate({
    inputRange: [0, 100],
    outputRange: [1, 0.9],
    extrapolate: 'clamp',
  });

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.background} />

      {/* Animated Header */}
      <Animated.View style={[styles.header, { opacity: headerOpacity }]}>
        <LinearGradient
          colors={[Colors.background, 'transparent']}
          style={styles.headerGradient}
        >
          <Text style={styles.logo}>Vibe<Text style={{ color: Colors.accentPink }}>Crush</Text></Text>
          <Text style={Typography.caption}>CLOUT MODE</Text>
        </LinearGradient>
      </Animated.View>

      {/* Feed */}
      <Animated.FlatList
        data={posts}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <VideoCard
            post={item}
            onReply={handleReply}
            onLike={handleLike}
            onBoost={(id) => setBoostTarget(id)}
          />
        )}
        contentContainerStyle={styles.feedContent}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh}
            tintColor={Colors.accentPink} />
        }
        onScroll={Animated.event(
          [{ nativeEvent: { contentOffset: { y: scrollY } } }],
          { useNativeDriver: true }
        )}
        // Empty state
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Text style={{ fontSize: 64, marginBottom: Spacing.md }}>🎬</Text>
            <Text style={Typography.h2}>No posts yet</Text>
            <Text style={[Typography.body, { textAlign: 'center', marginTop: Spacing.sm }]}>
              Be the first to post a video prompt{'\n'}and watch the replies flood in
            </Text>
          </View>
        }
      />

      {/* Boost Modal */}
      <BoostModal
        visible={!!boostTarget}
        onClose={() => setBoostTarget(null)}
        onSelect={handleBoostSelect}
        targetId={boostTarget || ''}
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
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 10,
  },
  headerGradient: {
    paddingTop: 60,
    paddingHorizontal: Spacing.lg,
    paddingBottom: Spacing.lg,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
  },
  logo: {
    fontSize: 28,
    fontWeight: '900',
    color: '#FFF',
    letterSpacing: -1,
  },
  feedContent: {
    paddingTop: 110,
    paddingHorizontal: Spacing.lg,
    paddingBottom: 100,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: SCREEN_HEIGHT * 0.2,
  },
});
