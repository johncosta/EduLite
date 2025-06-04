import React from "react";
import Button from "../components/common/Button";

// Demo page to showcase the Button component with different props
const ButtonDemo = () => (
  <div className="p-8 space-y-6 bg-gray-50 min-h-screen">
    <h1 className="text-2xl font-bold mb-4">Button Component Demo</h1>
    <div className="space-x-4">
      <Button onClick={() => alert('Primary clicked!')}>Primary (default)</Button>
      <Button type="secondary" onClick={() => alert('Secondary clicked!')}>Secondary</Button>
      <Button type="danger" onClick={() => alert('Danger clicked!')}>Danger</Button>
    </div>
    <div className="space-x-4">
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
    <div className="space-x-4">
      <Button disabled>Disabled</Button>
      <Button type="secondary" disabled>Disabled Secondary</Button>
      <Button type="danger" disabled>Disabled Danger</Button>
    </div>
    <div className="space-x-4">
      <Button className="uppercase tracking-widest">Custom Class</Button>
      <Button aria-label="Accessible Button">With aria-label</Button>
    </div>
  </div>
);

export default ButtonDemo;
