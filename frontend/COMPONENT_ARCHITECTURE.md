# Component Architecture

This document outlines the reusable component structure and auto-layout patterns used in the Sales Agent application.

## Layout Components

### Container
**Location:** `/src/app/components/ui/Container.tsx`
**Purpose:** Provides consistent max-width and horizontal padding across pages
**Props:**
- `maxWidth`: "sm" | "md" | "lg" | "xl" | "2xl" | "full"
- `className`: Additional CSS classes

**Usage:**
```tsx
<Container maxWidth="xl">
  {/* content */}
</Container>
```

### Grid
**Location:** `/src/app/components/ui/Grid.tsx`
**Purpose:** Responsive grid layout with configurable columns per breakpoint
**Props:**
- `cols`: Object with breakpoint keys (default, sm, md, lg, xl)
- `gap`: Spacing between grid items
- `className`: Additional CSS classes

**Usage:**
```tsx
<Grid cols={{ default: 1, md: 2, lg: 3 }} gap={6}>
  {/* grid items */}
</Grid>
```

### Stack
**Location:** `/src/app/components/ui/Stack.tsx`
**Purpose:** Flexbox-based vertical or horizontal layout
**Props:**
- `direction`: "vertical" | "horizontal"
- `gap`: Spacing between items
- `align`: Item alignment
- `justify`: Content justification

**Usage:**
```tsx
<Stack direction="vertical" gap={4} align="center">
  {/* stacked items */}
</Stack>
```

## UI Components

### BackgroundGradient
**Location:** `/src/app/components/ui/BackgroundGradient.tsx`
**Purpose:** Decorative background gradient effects
**Props:**
- `variant`: "default" | "subtle" | "centered"

**Usage:**
```tsx
<BackgroundGradient variant="subtle" />
```

### IconContainer
**Location:** `/src/app/components/ui/IconContainer.tsx`
**Purpose:** Consistent icon wrapper with gradient background
**Props:**
- `icon`: LucideIcon component
- `variant`: "square" | "circle"
- `size`: "sm" | "md" | "lg"

**Usage:**
```tsx
<IconContainer icon={Database} size="md" variant="square" />
```

### AppCard
**Location:** `/src/app/components/ui/AppCard.tsx`
**Purpose:** Reusable card component with consistent styling
**Props:**
- `hover`: Enable hover effects
- `padding`: "none" | "sm" | "md" | "lg"
- `onClick`: Click handler

**Usage:**
```tsx
<AppCard hover padding="md">
  {/* card content */}
</AppCard>
```

## Feature Components

### DatasetCard
**Location:** `/src/app/components/DatasetCard.tsx`
**Purpose:** Display dataset information with icon, stats, and action button
**Props:**
- `name`, `description`, `rows`, `columns`, `icon`, `onSelect`, `delay`

### ChatPanel
**Location:** `/src/app/components/ChatPanel.tsx`
**Purpose:** Complete chat interface with messages and input
**Props:**
- `initialMessages`: Array of initial chat messages

### ChatMessage
**Location:** `/src/app/components/ChatMessage.tsx`
**Purpose:** Individual chat message bubble
**Props:**
- `type`: "user" | "ai"
- `content`: Message text

### TypingIndicator
**Location:** `/src/app/components/TypingIndicator.tsx`
**Purpose:** Animated typing indicator for AI responses

### PageHeader
**Location:** `/src/app/components/PageHeader.tsx`
**Purpose:** Consistent page header with title, icon, and optional action
**Props:**
- `title`, `icon`, `action`

### UploadSection
**Location:** `/src/app/components/UploadSection.tsx`
**Purpose:** File upload area with drag-drop styling

### ChartCard
**Location:** `/src/app/components/ChartCard.tsx`
**Purpose:** Chart wrapper with consistent styling
**Props:**
- `title`, `type`: "line" | "bar" | "pie" | "area"

## Auto-Layout Patterns

### Responsive Breakpoints
All layout components use Tailwind's responsive breakpoints:
- **sm**: 640px
- **md**: 768px
- **lg**: 1024px
- **xl**: 1280px

### Flexible Layouts
- Dashboard uses `flex flex-col lg:flex-row` for responsive side-by-side layout
- Grid component automatically adjusts columns based on screen size
- Container ensures consistent max-width across all pages

### Spacing System
Consistent gap/padding scale:
- **4**: 1rem (16px)
- **6**: 1.5rem (24px)
- **8**: 2rem (32px)

## Benefits

1. **Consistency**: All components share the same visual language
2. **Maintainability**: Changes to shared components propagate automatically
3. **Responsiveness**: Auto-layout patterns handle different screen sizes
4. **Reusability**: Components can be easily composed in different contexts
5. **Type Safety**: Full TypeScript support with proper prop types
