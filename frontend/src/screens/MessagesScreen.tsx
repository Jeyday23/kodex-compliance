import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View, Text, StyleSheet, FlatList, TextInput,
  TouchableOpacity, KeyboardAvoidingView, Platform,
} from 'react-native';
import { Colors, Typography, Spacing, BorderRadius } from '../theme';
import { GlassCard } from '../components';
import { api } from '../services/api';

// === Conversation List ===
export const ConversationListScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [conversations, setConversations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const data = await api.getConversations();
      setConversations(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={[Typography.h1, { padding: Spacing.lg, paddingTop: 60 }]}>
        Messages 💬
      </Text>
      <FlatList
        data={conversations}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <TouchableOpacity
            onPress={() => navigation.navigate('Chat', { conversationId: item.id, partnerName: item.partner_name })}
          >
            <GlassCard style={styles.convoCard}>
              <View style={styles.avatar}>
                <Text style={{ fontSize: 24 }}>
                  {item.partner_name?.[0]?.toUpperCase() || '?'}
                </Text>
              </View>
              <View style={{ flex: 1, marginLeft: Spacing.md }}>
                <Text style={Typography.h3}>{item.partner_name}</Text>
                <Text style={[Typography.caption, { marginTop: 2 }]} numberOfLines={1}>
                  {item.last_message || 'Start the conversation...'}
                </Text>
              </View>
              {item.unread_count > 0 && (
                <View style={styles.badge}>
                  <Text style={{ color: '#FFF', fontSize: 12, fontWeight: '700' }}>
                    {item.unread_count}
                  </Text>
                </View>
              )}
            </GlassCard>
          </TouchableOpacity>
        )}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={{ fontSize: 48 }}>💌</Text>
            <Text style={[Typography.body, { textAlign: 'center', marginTop: Spacing.md }]}>
              No matches yet{'\n'}Reply to posts and get noticed!
            </Text>
          </View>
        }
      />
    </View>
  );
};

// === Chat Screen ===
export const ChatScreen: React.FC<{ route: any }> = ({ route }) => {
  const { conversationId, partnerName } = route.params;
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const flatListRef = useRef<FlatList>(null);

  useEffect(() => {
    loadMessages();
    const interval = setInterval(loadMessages, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  const loadMessages = async () => {
    try {
      const data = await api.getMessages(conversationId);
      setMessages(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    try {
      const msg = await api.sendMessage(conversationId, input.trim());
      setMessages(prev => [...prev, msg]);
      setInput('');
      flatListRef.current?.scrollToEnd({ animated: true });
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={90}
    >
      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={(item) => item.id}
        contentContainerStyle={{ padding: Spacing.lg, paddingBottom: 80 }}
        renderItem={({ item }) => {
          const isMine = item.sender_name === partnerName ? false : true;
          return (
            <View style={[styles.bubble, isMine ? styles.myBubble : styles.theirBubble]}>
              <Text style={{ color: '#FFF', fontSize: 15 }}>{item.body}</Text>
              <Text style={[Typography.caption, { marginTop: 4, fontSize: 10 }]}>
                {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </Text>
            </View>
          );
        }}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: false })}
      />
      <View style={styles.inputBar}>
        <TextInput
          style={styles.textInput}
          value={input}
          onChangeText={setInput}
          placeholder="Say something..."
          placeholderTextColor={Colors.textMuted}
          onSubmitEditing={handleSend}
        />
        <TouchableOpacity onPress={handleSend} style={styles.sendBtn}>
          <Text style={{ color: Colors.accentPink, fontSize: 18, fontWeight: '700' }}>↑</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  convoCard: { flexDirection: 'row', alignItems: 'center', marginHorizontal: Spacing.lg, marginBottom: Spacing.sm, padding: Spacing.md },
  avatar: { width: 48, height: 48, borderRadius: 24, backgroundColor: Colors.surface, alignItems: 'center', justifyContent: 'center' },
  badge: { backgroundColor: Colors.accentPink, borderRadius: 12, minWidth: 24, height: 24, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 6 },
  empty: { alignItems: 'center', paddingTop: 120 },
  bubble: { maxWidth: '75%', padding: Spacing.sm, borderRadius: 16, marginBottom: Spacing.sm },
  myBubble: { alignSelf: 'flex-end', backgroundColor: Colors.accentPink + 'CC', borderBottomRightRadius: 4 },
  theirBubble: { alignSelf: 'flex-start', backgroundColor: Colors.surface, borderBottomLeftRadius: 4 },
  inputBar: { flexDirection: 'row', alignItems: 'center', padding: Spacing.sm, paddingBottom: 34, backgroundColor: Colors.surface, borderTopWidth: 1, borderTopColor: Colors.border },
  textInput: { flex: 1, backgroundColor: Colors.background, borderRadius: 20, paddingHorizontal: Spacing.md, paddingVertical: 10, color: Colors.text, fontSize: 15 },
  sendBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: Colors.background, alignItems: 'center', justifyContent: 'center', marginLeft: Spacing.sm },
});
