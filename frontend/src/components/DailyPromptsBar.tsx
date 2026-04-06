import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { Colors, Typography, Spacing, BorderRadius } from '../theme';
import { api } from '../services/api';

interface Props {
  onSelectPrompt: (prompt: any) => void;
}

const CATEGORY_EMOJI: Record<string, string> = {
  flirty: '😏',
  bold: '🔥',
  funny: '😂',
  deep: '💭',
  chaotic: '🌀',
};

export const DailyPromptsBar: React.FC<Props> = ({ onSelectPrompt }) => {
  const [prompts, setPrompts] = useState<any[]>([]);

  useEffect(() => {
    api.getTodaysPrompts().then(setPrompts).catch(console.error);
  }, []);

  if (!prompts.length) return null;

  return (
    <View style={styles.container}>
      <Text style={[Typography.caption, { marginLeft: Spacing.lg, marginBottom: Spacing.xs }]}>
        TODAY'S PROMPTS
      </Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ paddingHorizontal: Spacing.md }}>
        {prompts.map((p) => (
          <TouchableOpacity key={p.id} style={styles.card} onPress={() => onSelectPrompt(p)}>
            <Text style={{ fontSize: 20 }}>{CATEGORY_EMOJI[p.category] || '🎯'}</Text>
            <Text style={styles.promptText} numberOfLines={2}>{p.text}</Text>
            <Text style={[Typography.caption, { marginTop: 4 }]}>
              {p.total_responses} replies
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { marginBottom: Spacing.md },
  card: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    marginHorizontal: Spacing.xs,
    width: 200,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  promptText: {
    color: Colors.text,
    fontSize: 14,
    fontWeight: '600',
    marginTop: Spacing.xs,
    lineHeight: 20,
  },
});
