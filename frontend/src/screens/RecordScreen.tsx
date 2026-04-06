import React, { useState, useRef, useEffect } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, TextInput,
  Dimensions, Animated, KeyboardAvoidingView, Platform,
} from 'react-native';
import { Camera, useCameraDevices } from 'react-native-vision-camera';
import LinearGradient from 'react-native-linear-gradient';
import { Colors, Gradients, Typography, Spacing, BorderRadius } from '../theme';
import { GradientButton } from '../components';
import { api } from '../services/api';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');
const MAX_DURATION = 30; // seconds

export const RecordScreen: React.FC<{ route: any; navigation: any }> = ({ route, navigation }) => {
  const { postId, mode } = route.params || {};
  const isReply = mode === 'reply';

  const [hasPermission, setHasPermission] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedVideo, setRecordedVideo] = useState<string | null>(null);
  const [promptText, setPromptText] = useState('');
  const [timer, setTimer] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [cameraFacing, setCameraFacing] = useState<'front' | 'back'>('front');

  const cameraRef = useRef<Camera>(null);
  const progressAnim = useRef(new Animated.Value(0)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const devices = useCameraDevices();
  const device = cameraFacing === 'front' ? devices.front : devices.back;

  useEffect(() => {
    Camera.requestCameraPermission().then((status) => {
      setHasPermission(status === 'granted');
    });
  }, []);

  useEffect(() => {
    if (isRecording) {
      // Pulse animation on record button
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, { toValue: 1.2, duration: 500, useNativeDriver: true }),
          Animated.timing(pulseAnim, { toValue: 1, duration: 500, useNativeDriver: true }),
        ])
      ).start();

      // Progress bar
      Animated.timing(progressAnim, {
        toValue: 1,
        duration: MAX_DURATION * 1000,
        useNativeDriver: false,
      }).start();

      // Timer
      timerRef.current = setInterval(() => {
        setTimer(prev => {
          if (prev >= MAX_DURATION - 1) {
            stopRecording();
            return MAX_DURATION;
          }
          return prev + 1;
        });
      }, 1000);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      pulseAnim.setValue(1);
      progressAnim.setValue(0);
    };
  }, [isRecording]);

  const startRecording = async () => {
    if (!cameraRef.current) return;
    setIsRecording(true);
    setTimer(0);
    try {
      const video = await cameraRef.current.startRecording({
        onRecordingFinished: (v) => setRecordedVideo(v.path),
        onRecordingError: (e) => console.error(e),
      });
    } catch {}
  };

  const stopRecording = async () => {
    if (!cameraRef.current) return;
    setIsRecording(false);
    await cameraRef.current.stopRecording();
  };

  const handlePublish = async () => {
    if (!recordedVideo) return;
    setUploading(true);
    try {
      // 1. Get presigned upload URL
      const { upload_url, key } = await api.getUploadUrl();

      // 2. Upload video to S3
      const videoBlob = await fetch(recordedVideo).then(r => r.blob());
      await fetch(upload_url, {
        method: 'PUT',
        body: videoBlob,
        headers: { 'Content-Type': 'video/mp4' },
      });

      // 3. Create post or reply
      if (isReply && postId) {
        await api.createReply(postId, { video_key: key, duration_seconds: timer });
      } else {
        await api.createPost({ video_key: key, prompt_text: promptText, duration_seconds: timer });
      }

      navigation.goBack();
    } catch (err) {
      console.error('Publish error:', err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <View style={styles.container}>
      {/* Camera Preview */}
      {device && hasPermission && (
        <Camera
          ref={cameraRef}
          style={StyleSheet.absoluteFill}
          device={device}
          isActive={true}
          video={true}
          audio={true}
        />
      )}

      {/* Dark overlay gradient */}
      <LinearGradient
        colors={['rgba(0,0,0,0.4)', 'transparent', 'rgba(0,0,0,0.6)']}
        locations={[0, 0.4, 1]}
        style={StyleSheet.absoluteFill}
      />

      {/* Top bar */}
      <View style={styles.topBar}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.closeBtn}>✕</Text>
        </TouchableOpacity>
        <Text style={[Typography.caption, { color: '#FFF' }]}>
          {isReply ? 'RECORD REPLY' : 'NEW POST'}
        </Text>
        <TouchableOpacity onPress={() => setCameraFacing(f => f === 'front' ? 'back' : 'front')}>
          <Text style={{ fontSize: 24 }}>🔄</Text>
        </TouchableOpacity>
      </View>

      {/* Recording progress bar */}
      {isRecording && (
        <Animated.View style={[styles.progressBar, {
          width: progressAnim.interpolate({
            inputRange: [0, 1],
            outputRange: ['0%', '100%'],
          }),
        }]}>
          <LinearGradient colors={Gradients.fire} style={{ flex: 1 }} start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }} />
        </Animated.View>
      )}

      {/* Timer */}
      {isRecording && (
        <View style={styles.timerContainer}>
          <View style={styles.timerDot} />
          <Text style={styles.timerText}>
            {String(Math.floor(timer / 60)).padStart(2, '0')}:{String(timer % 60).padStart(2, '0')}
          </Text>
        </View>
      )}

      {/* Bottom controls */}
      <View style={styles.bottomControls}>
        {!recordedVideo ? (
          <>
            {/* Prompt input (only for new posts) */}
            {!isReply && !isRecording && (
              <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
                <View style={styles.promptInput}>
                  <TextInput
                    placeholder="Write your prompt..."
                    placeholderTextColor={Colors.textMuted}
                    value={promptText}
                    onChangeText={setPromptText}
                    style={styles.textInput}
                    maxLength={120}
                  />
                </View>
              </KeyboardAvoidingView>
            )}

            {/* Record button */}
            <View style={styles.recordRow}>
              <TouchableOpacity
                onPress={isRecording ? stopRecording : startRecording}
                activeOpacity={0.8}
              >
                <Animated.View style={[
                  styles.recordBtn,
                  isRecording && styles.recordBtnActive,
                  { transform: [{ scale: isRecording ? pulseAnim : 1 }] },
                ]}>
                  {isRecording ? (
                    <View style={styles.stopSquare} />
                  ) : (
                    <LinearGradient colors={Gradients.fire} style={styles.recordInner} />
                  )}
                </Animated.View>
              </TouchableOpacity>
            </View>
          </>
        ) : (
          /* Post-recording: publish */
          <View style={styles.publishRow}>
            <TouchableOpacity onPress={() => { setRecordedVideo(null); setTimer(0); }}>
              <Text style={[Typography.button, { color: Colors.textSecondary }]}>Retake</Text>
            </TouchableOpacity>
            <GradientButton
              title={isReply ? 'Send Reply' : 'Post It 🔥'}
              variant="fire"
              size="lg"
              onPress={handlePublish}
              loading={uploading}
            />
          </View>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  topBar: {
    position: 'absolute',
    top: 60,
    left: Spacing.lg,
    right: Spacing.lg,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    zIndex: 10,
  },
  closeBtn: {
    fontSize: 24,
    color: '#FFF',
    fontWeight: '300',
  },
  progressBar: {
    position: 'absolute',
    top: 56,
    left: 0,
    height: 3,
    zIndex: 20,
  },
  timerContainer: {
    position: 'absolute',
    top: 100,
    alignSelf: 'center',
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)',
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.full,
  },
  timerDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: Colors.error,
    marginRight: Spacing.sm,
  },
  timerText: {
    color: '#FFF',
    fontWeight: '700',
    fontSize: 16,
    fontVariant: ['tabular-nums'],
  },
  bottomControls: {
    position: 'absolute',
    bottom: 40,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  promptInput: {
    width: SCREEN_WIDTH - Spacing.xl * 2,
    marginBottom: Spacing.lg,
  },
  textInput: {
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: BorderRadius.lg,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.md,
    color: '#FFF',
    fontSize: 16,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  recordRow: {
    alignItems: 'center',
  },
  recordBtn: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 4,
    borderColor: 'rgba(255,255,255,0.5)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  recordBtnActive: {
    borderColor: Colors.error,
  },
  recordInner: {
    width: 60,
    height: 60,
    borderRadius: 30,
  },
  stopSquare: {
    width: 28,
    height: 28,
    borderRadius: 6,
    backgroundColor: Colors.error,
  },
  publishRow: {
    width: SCREEN_WIDTH - Spacing.xl * 2,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
});
