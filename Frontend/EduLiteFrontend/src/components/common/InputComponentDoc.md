# Input Component Documentation

## Overview

The `Input` component is a reusable, Apple-style form input with glass-morphism effects, dark mode support, and comprehensive validation features. It follows the established design system and provides a consistent user experience across the application.

## Installation & Import

```jsx
import Input from "../components/common/Input";
```

## Basic Usage

```jsx
import React, { useState } from "react";
import Input from "../components/common/Input";

function MyForm() {
  const [email, setEmail] = useState("");

  return (
    <Input
      type="email"
      name="email"
      label="Email Address"
      placeholder="Enter your email"
      value={email}
      onChange={(e) => setEmail(e.target.value)}
    />
  );
}
```

## Props

### Required Props

| Prop       | Type       | Description                                           |
| ---------- | ---------- | ----------------------------------------------------- |
| `type`     | `string`   | Input type ('text', 'email', 'password', 'tel', etc.) |
| `name`     | `string`   | Unique name for the input field                       |
| `value`    | `string`   | Current input value (controlled component)            |
| `onChange` | `function` | Function to handle value changes                      |

### Optional Props

| Prop          | Type      | Default | Description                          |
| ------------- | --------- | ------- | ------------------------------------ |
| `label`       | `string`  | `""`    | Label text displayed above the input |
| `placeholder` | `string`  | `""`    | Placeholder text inside the input    |
| `error`       | `string`  | `""`    | Error message to display below input |
| `disabled`    | `boolean` | `false` | Whether the input is disabled        |
| `required`    | `boolean` | `false` | Whether the field is required        |
| `className`   | `string`  | `""`    | Additional CSS classes               |

## Examples

### 1. Basic Text Input

```jsx
<Input
  type="text"
  name="username"
  label="Username"
  placeholder="Enter username"
  value={username}
  onChange={(e) => setUsername(e.target.value)}
/>
```

### 2. Email with Validation

```jsx
const [email, setEmail] = useState("");
const [emailError, setEmailError] = useState("");

const handleEmailChange = (e) => {
  const value = e.target.value;
  setEmail(value);
  setEmailError(
    value && !value.includes("@") ? "Please enter a valid email address" : ""
  );
};

<Input
  type="email"
  name="email"
  label="Email Address"
  placeholder="user@example.com"
  value={email}
  onChange={handleEmailChange}
  error={emailError}
/>;
```

### 3. Password Input

```jsx
<Input
  type="password"
  name="password"
  label="Password"
  placeholder="Enter your password"
  value={password}
  onChange={(e) => setPassword(e.target.value)}
  required
/>
```

### 4. Phone Number with Validation

```jsx
const [phone, setPhone] = useState("");
const [phoneError, setPhoneError] = useState("");

const handlePhoneChange = (e) => {
  const value = e.target.value;
  const phoneRegex = /^[\d\s\-\(\)]*$/;

  if (phoneRegex.test(value) || value === "") {
    setPhone(value);
    setPhoneError("");
  } else {
    setPhoneError("Only numbers and phone formatting characters allowed");
  }
};

<Input
  type="tel"
  name="phone"
  label="Phone Number"
  placeholder="(555) 123-4567"
  value={phone}
  onChange={handlePhoneChange}
  error={phoneError}
/>;
```

### 5. Disabled Input

```jsx
<Input
  type="text"
  name="readonly"
  label="Read Only Field"
  value="Cannot edit this"
  onChange={() => {}}
  disabled
/>
```

## Validation Examples

### Email Validation

```jsx
const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

const handleEmailChange = (e) => {
  const value = e.target.value;
  setEmail(value);

  if (value && !validateEmail(value)) {
    setEmailError("Please enter a valid email address");
  } else {
    setEmailError("");
  }
};
```

### Phone Number Validation

```jsx
const validatePhone = (phone) => {
  // Remove all non-digit characters for validation
  const cleanPhone = phone.replace(/\D/g, "");
  return cleanPhone.length >= 10;
};

const handlePhoneChange = (e) => {
  const value = e.target.value;
  // Allow only numbers and formatting characters
  const phoneRegex = /^[\d\s\-\(\)]*$/;

  if (phoneRegex.test(value) || value === "") {
    setPhone(value);
    if (value && !validatePhone(value)) {
      setPhoneError("Phone number must have at least 10 digits");
    } else {
      setPhoneError("");
    }
  } else {
    setPhoneError("Only numbers and phone formatting allowed");
  }
};
```

### Password Strength Validation

```jsx
const validatePassword = (password) => {
  const minLength = password.length >= 8;
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);

  if (!minLength) return "Password must be at least 8 characters";
  if (!hasUpper) return "Password must contain an uppercase letter";
  if (!hasLower) return "Password must contain a lowercase letter";
  if (!hasNumber) return "Password must contain a number";

  return "";
};

const handlePasswordChange = (e) => {
  const value = e.target.value;
  setPassword(value);
  setPasswordError(validatePassword(value));
};
```

## Form Library Integration

The Input component uses `React.forwardRef`, making it compatible with form libraries like React Hook Form:

```jsx
import { useForm } from "react-hook-form";

function MyForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Input
        {...register("email", {
          required: "Email is required",
          pattern: {
            value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            message: "Invalid email address",
          },
        })}
        type="email"
        name="email"
        label="Email Address"
        error={errors.email?.message}
      />
    </form>
  );
}
```

## Styling & Design System

The Input component follows the established Apple-style design system:

- **Glass-morphism**: `backdrop-blur-xl` with translucent backgrounds
- **Rounded corners**: `rounded-2xl` for modern appearance
- **Smooth animations**: Hover and focus transitions
- **Dark mode support**: Automatic theme switching
- **Accessibility**: Proper ARIA attributes and semantic markup

## Best Practices

### Do's ✅

- Always use controlled components with `value` and `onChange`
- Provide meaningful labels for accessibility
- Use appropriate input types (`email`, `tel`, `password`)
- Implement proper validation with error messages
- Use `React.forwardRef` for form library compatibility

### Don'ts ❌

- Don't use without proper state management
- Don't forget to handle validation errors
- Don't use generic 'text' for specialized inputs
- Don't skip accessibility attributes
- Don't override core styling without good reason

## Accessibility Features

- Semantic HTML with proper `input` elements
- Associated labels using `htmlFor` and `id`
- ARIA attributes for error states
- Keyboard navigation support
- Screen reader friendly error messages
- Focus management and visual indicators

## Browser Support

The Input component supports all modern browsers with CSS Grid and Flexbox support:

- Chrome 57+
- Firefox 52+
- Safari 10.1+
- Edge 16+

## Troubleshooting

### Common Issues

1. **Input not updating**: Ensure you're using controlled components with proper state
2. **Styling conflicts**: Check for CSS specificity issues with custom classes
3. **Form library issues**: Make sure you're using `React.forwardRef` properly
4. **Validation not working**: Verify your validation logic and error state management

### Performance Tips

- Use `useCallback` for event handlers to prevent unnecessary re-renders
- Implement debounced validation for expensive operations
- Consider memoization for complex validation logic
