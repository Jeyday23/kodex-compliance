import React, { useState, useRef, useEffect } from 'react';
import {
  View, Text, StyleSheet, TextInput, Dimensions,
  Animated, KeyboardAvoidingView, Platform,
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import { Colors, Gradients, Typography, Spacing, BorderRadius } from '../theme';
import { GradientButton } from '../components';
import { api, setToken } from '../services/api';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

export const LoginScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState<'phone' | 'otp'>('phone');
  const [loading, setLoading] = useState(false);

  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, { toValue: 1, duration: 800, useNativeDriver: true }),
      Animated.spring(slideAnim, { toValue: 0, friction: 8, useNativeDriver: true }),
    ]).start();
  }, []);

  const handleLogin = async () => {
    setLoading(true);
    try {
      const result = await api.login(phone, otp);
      setToken(result.access_token);
      navigation.reset({ index: 0, routes: [{ name: 'Main' }] });
    } catch (err) {
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <LinearGradient colors={['#0A0A0F', '#1a0a2e', '#0A0A0F']} style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.inner}
      >
        {/* Animated background glow */}
        <View style={styles.glowOrb} />
        <View style={[styles.glowOrb, styles.glowOrb2]} />

        <Animated.View style={[
          styles.content,
          { opacity: fadeAnim, transform: [{ translateY: slideAnim }] },
        ]}>
          {/* Logo */}
          <Text style={styles.logo}>
            Vibe<Text style={{ color: Colors.accentPink }}>Crush</Text>
          </Text>
          <Text style={styles.tagline}>Where attention is currency</Text>

          {/* Input card */}
          <View style={styles.inputCard}>
            {step === 'phone' ? (
              <>
                <Text style={[Typography.h3, { marginBottom: Spacing.md }]}>
                  Enter your number
                </Text>
                <View style={styles.inputRow}>
                  <View style={styles.countryCode}>
                    <Text style={styles.countryText}>🇩🇪 +49</Text>
                  </View>
                  <TextInput
                    style={styles.input}
                    placeholder="Phone number"
                    placeholderTextColor={Colors.textMuted}
                    value={phone}
                    onChangeText={setPhone}
                    keyboardType="phone-pad"
                    autoFocus
                  />
                </View>
                <GradientButton
                  title="Continue"
                  variant="fire"
                  size="lg"
                  onPress={() => setStep('otp')}
                  disabled={phone.length < 6}
                  style={{ marginTop: Spacing.lg }}
                />
              </>
            ) : (
              <>
                <Text style={[Typography.h3, { marginBottom: Spacing.md }]}>
                  Enter the code
                </Text>
                <Text style={[Typography.body, { marginBottom: Spacing.lg }]}>
                  Sent to +49 {phone}
                </Text>
                <View style={styles.otpRow}>
                  {[0, 1, 2, 3, 4, 5].map((i) => (
                    <View key={i} style={[
                      styles.otpBox,
                      otp.length > i && styles.otpBoxFilled,
                    ]}>
                      <Text style={styles.otpDigit}>{otp[i] || ''}</Text>
                    </View>
                  ))}
                </View>
                <TextInput
                  style={styles.hiddenInput}
                  value={otp}
                  onChangeText={(t) => setOtp(t.slice(0, 6))}
                  keyboardType="number-pad"
                  autoFocus
                />
                <GradientButton
                  title="Verify & Enter"
                  variant="primary"
                  size="lg"
                  onPress={handleLogin}
                  loading={loading}
                  disabled={otp.length < 6}
                  style={{ marginTop: Spacing.lg }}
                />
              </>
            )}
          </View>

          <Text style={styles.disclaimer}>
            By continuing, you agree to our Terms & Privacy Policy
          </Text>
        </Animated.View>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  inner: {
    flex: 1,
    justifyContent: 'center',
  },
  glowOrb: {
    position: 'absolute',
    width: 300,
    height: 300,
    borderRadius: 150,
    backgroundColor: 'rgba(255, 59, 122, 0.08)',
    top: SCREEN_HEIGHT * 0.15,
    left: -50,
    // Blur simulated with opacity
  },
  glowOrb2: {
    backgroundColor: 'rgba(139, 92, 246, 0.08)',
    top: SCREEN_HEIGHT * 0.5,
    right: -80,
    left: undefined,
  },
  content: {
    paddingHorizontal: Spacing.lg,
    alignItems: 'center',
  },
  logo: {
    fontSize: 48,
    fontWeight: '900',
    color: '#FFF',
    letterSpacing: -2,
    marginBottom: Spacing.xs,
  },
  tagline: {
    ...Typography.body,
    fontSize: 16,
    color: Colors.textSecondary,
    marginBottom: Spacing.xxl,
  },
  inputCard: {
    width: '100%',
    backgroundColor: Colors.surfaceGlass,
    borderRadius: BorderRadius.xl,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  inputRow: {
    flexDirection: 'row',
    gap: Spacing.sm,
  },
  countryCode: {
    backgroundColor: Colors.surfaceLight,
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.md,
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  countryText: {
    color: '#FFF',
    fontSize: 15,
  },
  input: {
    flex: 1,
    backgroundColor: Colors.surfaceLight,
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.md,
    color: '#FFF',
    fontSize: 18,
    fontWeight: '600',
    letterSpacing: 1,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  otpRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: Spacing.sm,
  },
  otpBox: {
    width: 48,
    height: 56,
    borderRadius: BorderRadius.md,
    backgroundColor: Colors.surfaceLight,
    borderWidth: 1.5,
    borderColor: 'rgba(255,255,255,0.06)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  otpBoxFilled: {
    borderColor: Colors.accentPink,
    backgroundColor: 'rgba(255,59,122,0.08)',
  },
  otpDigit: {
    color: '#FFF',
    fontSize: 22,
    fontWeight: '700',
  },
  hiddenInput: {
    position: 'absolute',
    opacity: 0,
    width: 1,
    height: 1,
  },
  disclaimer: {
    ...Typography.caption,
    fontSize: 11,
    textAlign: 'center',
    marginTop: Spacing.xl,
    color: Colors.textMuted,
  },
});
