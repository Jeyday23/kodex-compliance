import { StyleSheet } from 'react-native';

export const Typography = StyleSheet.create({
  h1: {
    fontSize: 32,
    fontWeight: '800',
    color: '#FFFFFF',
    letterSpacing: -0.5,
  },
  h2: {
    fontSize: 24,
    fontWeight: '700',
    color: '#FFFFFF',
    letterSpacing: -0.3,
  },
  h3: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  body: {
    fontSize: 15,
    fontWeight: '400',
    color: '#9898B0',
    lineHeight: 22,
  },
  caption: {
    fontSize: 12,
    fontWeight: '500',
    color: '#5C5C72',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  button: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF',
    letterSpacing: 0.5,
  },
  stat: {
    fontSize: 20,
    fontWeight: '800',
    color: '#FFFFFF',
  },
});
