# Feedback Notification Badges

## Overview
Added notification badges to the feedback menu items in all dashboards (Admin, Staff, Student) to indicate when there are new feedbacks or replies.

## Features

### Admin Dashboard
- **Student Feedback**: Shows red badge with count of unread student feedbacks (feedbacks without replies)
- **Staff Feedback**: Shows red badge with count of unread staff feedbacks (feedbacks without replies)

### Staff Dashboard  
- **Feedback**: Shows red badge with count of feedback replies from admin

### Student Dashboard
- **Feedback**: Shows red badge with count of feedback replies from admin

## Visual Design
- **Badge Color**: Red (`badge-danger`)
- **Position**: Right side of menu item
- **Animation**: Subtle pulse effect to draw attention
- **Size**: Small circular badge with count number

## How It Works

### For Admin:
- Badge appears when students/staff submit new feedback
- Count shows number of feedbacks awaiting reply
- Badge disappears when admin replies to all feedbacks

### For Staff/Students:
- Badge appears when admin replies to their feedback
- Count shows number of feedback replies received
- Badge indicates there are responses to check

## Technical Implementation

### Model Methods:
- `Admin.get_unread_student_feedbacks()`: Counts feedbacks with empty replies
- `Admin.get_unread_staff_feedbacks()`: Counts feedbacks with empty replies  
- `Staff.get_unread_feedback_replies()`: Counts feedbacks with non-empty replies
- `Student.get_unread_feedback_replies()`: Counts feedbacks with non-empty replies

### Template Integration:
- Added badge elements to sidebar template
- Used Django template tags to call model methods
- Conditional display based on count > 0

### CSS Styling:
- Custom CSS for badge positioning and animation
- Pulse animation to make badges more noticeable
- Responsive design for different screen sizes

## Usage Examples

### Admin sees:
- "Student Feedback (3)" - 3 new student feedbacks to review
- "Staff Feedback (1)" - 1 new staff feedback to review

### Student sees:
- "Feedback (2)" - 2 replies from admin to check

### Staff sees:
- "Feedback (1)" - 1 reply from admin to check

## Benefits
1. **Immediate Awareness**: Users know when there are new feedbacks/replies
2. **Better Communication**: Encourages timely responses
3. **Visual Feedback**: Clear indication of pending actions
4. **User Experience**: Reduces need to check empty feedback sections
5. **Engagement**: Animated badges draw attention to important updates

## Future Enhancements
- Mark replies as "read" when viewed
- Different badge colors for different priority levels
- Email notifications when badges appear
- Sound notifications for real-time updates