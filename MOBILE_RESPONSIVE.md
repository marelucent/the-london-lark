# Mobile Responsive Design - London Lark

## Breakpoints

- **Mobile**: < 768px (iPhone SE: 375px, iPhone 12: 390px, etc.)
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## Key Features Implemented

### 1. Mobile (< 768px)
- ✓ Reduced padding (1rem vs 2rem)
- ✓ Font size: 16px minimum (prevents iOS zoom)
- ✓ Stacked button layout (vertical)
- ✓ Full-width buttons with 48px min-height (touch-friendly)
- ✓ Removed side margins on messages
- ✓ Smaller header (1.8rem vs 2.8rem)
- ✓ Touch-friendly footer links (padding for tap target)
- ✓ Full-width mood tuner panel
- ✓ Disabled hover effects (touch devices don't hover)
- ✓ Active states for touch feedback

### 2. Tablet (768px - 1024px)
- ✓ Medium padding (1.5rem)
- ✓ Side-by-side buttons with flexbox
- ✓ Partial-width mood tuner (320px)
- ✓ Moderate font sizes
- ✓ Touch-friendly 48px button heights

### 3. Desktop (> 1024px)
- ✓ Original spacing and sizing
- ✓ Hover effects enabled
- ✓ Max width: 720px container

### 4. Touch Device Optimizations
- ✓ Media query for (hover: none) and (pointer: coarse)
- ✓ Removed all hover transforms on touch devices
- ✓ Ensured 44x44px minimum tap targets
- ✓ Active states with scale(0.98) for visual feedback

### 5. About Page
- ✓ Responsive typography
- ✓ Full-width "Ask the Lark" button on mobile
- ✓ Adjusted spacing for mobile
- ✓ Touch-friendly tap targets

## Typography Scale

### Mobile
- Body: 16px (prevents iOS zoom)
- H1: 1.8rem
- Message text: 1rem
- Line height: 1.75

### Tablet
- H1: 2.2rem
- Message text: 1.05rem

### Desktop
- H1: 2.8rem
- Message text: 1.1rem
- Line height: 1.9

## Touch Targets

All interactive elements meet WCAG 2.1 Level AA:
- Buttons: 48px min-height
- Links: 44px min tap area
- Mood tuner toggle: 44px min-height
- Footer links: 0.8rem padding for larger tap area

## Testing Checklist

To test responsive design:

1. **Browser DevTools**:
   - Open DevTools (F12)
   - Toggle device toolbar (Ctrl+Shift+M)
   - Test at: 375px, 768px, 1024px, 1440px

2. **Key Breakpoints**:
   - [ ] 375px (iPhone SE) - buttons stack, text readable
   - [ ] 390px (iPhone 12) - no horizontal scroll
   - [ ] 768px (iPad) - buttons side-by-side
   - [ ] 1024px (iPad Pro) - desktop layout begins
   - [ ] 1440px+ (Desktop) - centered container

3. **Features to Verify**:
   - [ ] Buttons stack vertically on mobile
   - [ ] No horizontal scrolling
   - [ ] Text is readable without zooming
   - [ ] Touch targets are easy to tap
   - [ ] Venue cards are readable
   - [ ] About page is responsive
   - [ ] Mood tuner works on mobile (full width)
   - [ ] No hover effects on touch devices

## Notes

- iOS Safari: 16px font prevents auto-zoom on input focus
- Touch devices: No hover states, use active states instead
- Landscape mobile: Reduced padding to maximize space
- All animations preserved but work at all sizes
