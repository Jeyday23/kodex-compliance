import React, { useState, useEffect } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  Image, StatusBar,
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import { Colors, Gradients, Typography, Spacing, BorderRadius } from '../theme';
import { GlassCard, CloutMeter, TierBadge, GradientButton } from '../components';
import { api } from '../services/api';

export const ProfileScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    api.getMe().then(setUser).catch(console.error);
  }, []);

  if (!user) return (
    <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
      <Text style={{ fontSize: 40 }}>✨</Text>
    </View>
  );

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <StatusBar barStyle="light-content" />

      {/* Hero gradient header */}
      <LinearGradient colors={Gradients.primary} style={styles.hero}>
        <View style={styles.avatarContainer}>
          {user.avatar_url ? (
            <Image source={{ uri: user.avatar_url }} style={styles.avatar} />
          ) : (
            <LinearGradient colors={Gradients.fire} style={styles.avatar}>
              <Text style={{ fontSize: 40 }}>
                {user.display_name?.[0]?.toUpperCase() || '?'}
              </Text>
            </LinearGradient>
          )}
          <TierBadge tier={user.tier} size="md" />
        </View>
        <Text style={[Typography.h1, { textAlign: 'center', marginTop: Spacing.md }]}>
          {user.display_name}
        </Text>
        {user.is_anchor && (
          <View style={styles.anchorBadge}>
            <Text style={styles.anchorText}>⭐ TOP CREATOR</Text>
          </View>
        )}
      </LinearGradient>

      <View style={styles.content}>
        {/* Clout Score Card */}
        <GlassCard glow style={{ marginBottom: Spacing.lg }}>
          <CloutMeter score={user.clout_score} tier={user.tier} />
        </GlassCard>

        {/* Stats Grid */}
        <View style={styles.statsGrid}>
          <GlassCard style={styles.statCard}>
            <Text style={Typography.stat}>{user.clout_score.toFixed(0)}</Text>
            <Text style={Typography.caption}>Clout</Text>
          </GlassCard>
          <GlassCard style={styles.statCard}>
            <Text style={Typography.stat}>{user.tier}</Text>
            <Text style={Typography.caption}>Tier</Text>
          </GlassCard>
        </View>

        {/* Elite subscription */}
        {!user.is_elite && (
          <GlassCard glow style={{ marginTop: Spacing.lg }}>
            <View style={{ alignItems: 'center', paddingVertical: Spacing.md }}>
              <Text style={{ fontSize: 32, marginBottom: Spacing.sm }}>👑</Text>
              <Text style={Typography.h3}>Go Elite</Text>
              <Text style={[Typography.body, { textAlign: 'center', marginVertical: Spacing.sm }]}>
                Get shown to high-tier users{'\n'}€9.99/month
              </Text>
              <GradientButton
                title="Upgrade Now"
                variant="gold"
                onPress={() => {/* Stripe checkout */}}
              />
            </View>
          </GlassCard>
        )}

        {/* Settings */}
        <TouchableOpacity style={styles.settingsRow}>
          <Text style={Typography.body}>Edit Profile</Text>
          <Text style={{ color: Colors.textMuted }}>›</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.settingsRow}>
          <Text style={Typography.body}>Privacy & Safety</Text>
          <Text style={{ color: Colors.textMuted }}>›</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  hero: {
    paddingTop: 80,
    paddingBottom: Spacing.xl,
    alignItems: 'center',
    borderBottomLeftRadius: BorderRadius.xl,
    borderBottomRightRadius: BorderRadius.xl,
  },
  avatarContainer: {
    position: 'relative',
  },
  avatar: {
    width: 100,
    height: 100,
    borderRadius: 50,
    borderWidth: 3,
    borderColor: '#FFF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  anchorBadge: {
    backgroundColor: 'rgba(255,215,0,0.2)',
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.full,
    marginTop: Spacing.sm,
  },
  anchorText: {
    color: Colors.accentGold,
    fontWeight: '800',
    fontSize: 12,
    letterSpacing: 1,
  },
  content: {
    padding: Spacing.lg,
  },
  statsGrid: {
    flexDirection: 'row',
    gap: Spacing.md,
  },
  statCard: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: Spacing.lg,
  },
  settingsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
  },
});
