import 'react-native-gesture-handler';
import React from 'react';
import { Ionicons } from '@expo/vector-icons';
import { DarkTheme, NavigationContainer, Theme as NavigationTheme } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';
import {
  FeedScreen, LoginScreen, ProfileScreen, RecordScreen,
  RepliesScreen, ConversationListScreen, ChatScreen, NotificationsScreen,
} from './src/screens';
import { colors } from './src/theme/colors';

type RootStackParamList = {
  Login: undefined;
  Main: undefined;
  Replies: undefined;
  Chat: { conversationId: string; partnerName: string };
};
type MainTabParamList = {
  Feed: undefined;
  Record: undefined;
  Messages: undefined;
  Notifications: undefined;
  Profile: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();

const navigationTheme: NavigationTheme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    background: colors.background,
    card: colors.surface,
    text: colors.text,
    border: colors.border,
    primary: colors.accent,
    notification: colors.accent,
  },
};

function MainTabs() {
  return (
    <Tab.Navigator screenOptions={({ route }) => ({
      headerShown: false,
      tabBarActiveTintColor: colors.accent,
      tabBarInactiveTintColor: colors.textMuted,
      tabBarStyle: { backgroundColor: colors.surface, borderTopColor: colors.border },
      tabBarIcon: ({ color, size }) => {
        const iconMap: Record<keyof MainTabParamList, keyof typeof Ionicons.glyphMap> = {
          Feed: 'home',
          Record: 'radio-button-on',
          Messages: 'chatbubbles',
          Notifications: 'notifications',
          Profile: 'person',
        };
        return <Ionicons name={iconMap[route.name]} size={size} color={color} />;
      },
    })}>
      <Tab.Screen name="Feed" component={FeedScreen} />
      <Tab.Screen name="Record" component={RecordScreen} />
      <Tab.Screen name="Messages" component={ConversationListScreen} />
      <Tab.Screen name="Notifications" component={NotificationsScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

export default function App() {
  return (
    <NavigationContainer theme={navigationTheme}>
      <StatusBar style="light" />
      <Stack.Navigator
        initialRouteName="Login"
        screenOptions={{
          headerStyle: { backgroundColor: colors.surface },
          headerTintColor: colors.text,
          contentStyle: { backgroundColor: colors.background },
        }}
      >
        <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />
        <Stack.Screen name="Main" component={MainTabs} options={{ headerShown: false }} />
        <Stack.Screen name="Replies" component={RepliesScreen} options={{ title: 'Replies', headerBackTitle: 'Back' }} />
        <Stack.Screen name="Chat" component={ChatScreen} options={({ route }) => ({
          title: (route.params as any)?.partnerName || 'Chat',
          headerBackTitle: 'Back',
        })} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
