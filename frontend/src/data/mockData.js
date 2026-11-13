/**
 * Phase 1 Mock & Demonstration Data
 * ---------------------------------
 * This file contains strictly labeled mock dataset used exclusively for visual shell verification
 * and UI component styling in Phase 1 before live algorithmic logic (DFA/LPM/Dispatch) is connected.
 */

export const MOCK_STAT_CARDS = [
  {
    title: 'Active Incidents',
    value: '04',
    change: '+1 today',
    trend: 'up',
    color: 'orange',
    subtext: 'Pending authority action'
  },
  {
    title: 'Total Reports Filed',
    value: '28',
    change: '+14% vs avg',
    trend: 'neutral',
    color: 'blue',
    subtext: 'Current semester session'
  },
  {
    title: 'Critical Escalations',
    value: '02',
    change: 'Immediate attention',
    trend: 'warning',
    color: 'rose',
    subtext: 'Medical & missing booklets'
  },
  {
    title: 'Subnets Monitored',
    value: '06',
    change: '100% operational',
    trend: 'up',
    color: 'emerald',
    subtext: '4 campus blocks + labs'
  }
];

export const MOCK_INCIDENT_TIMELINE = [
  { time: '14:25', id: 'REP-2026-004', type: 'Missing-Script', hall: 'HALL-102', status: 'Submitted', badge: 'critical' },
  { time: '13:50', id: 'REP-2026-003', type: 'Technical', hall: 'LAB-3', status: 'Resolved', badge: 'neutral' },
  { time: '11:15', id: 'REP-2026-002', type: 'Medical', hall: 'HALL-204', status: 'In-Progress', badge: 'critical' },
  { time: '09:40', id: 'REP-2026-001', type: 'Malpractice', hall: 'HALL-401', status: 'Assigned', badge: 'warning' },
];

export const MOCK_ANALYTICS_HOURLY = [
  { time: '09:00', Malpractice: 1, Technical: 2, Medical: 0, Disturbance: 1 },
  { time: '10:00', Malpractice: 3, Technical: 1, Medical: 1, Disturbance: 0 },
  { time: '11:00', Malpractice: 2, Technical: 3, Medical: 2, Disturbance: 1 },
  { time: '12:00', Malpractice: 0, Technical: 1, Medical: 0, Disturbance: 0 },
  { time: '13:00', Malpractice: 1, Technical: 2, Medical: 0, Disturbance: 2 },
  { time: '14:00', Malpractice: 4, Technical: 2, Medical: 1, Disturbance: 1 },
  { time: '15:00', Malpractice: 2, Technical: 0, Medical: 0, Disturbance: 0 },
];

export const MOCK_ANALYTICS_CATEGORIES = [
  { name: 'Malpractice (IR01)', count: 12, color: '#f97316' },
  { name: 'Disturbance (IR02)', count: 5, color: '#eab308' },
  { name: 'Medical (IR03)', count: 4, color: '#ef4444' },
  { name: 'Technical (IR04)', count: 8, color: '#3b82f6' },
  { name: 'Missing-Script (IR05)', count: 3, color: '#8b5cf6' },
];

