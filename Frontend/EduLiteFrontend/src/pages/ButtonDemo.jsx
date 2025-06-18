import React from "react";
import Button from "../components/common/Button"; // Assuming this path is correct

// Demo page to showcase the Button component with different props
const ButtonDemo = () => (
  <div className="p-8 space-y-6 bg-gray-50 min-h-screen">
    <h1 className="text-2xl font-bold mb-6">Button Component Demo</h1>

    {/* Type Variations */}
    <div>
      <h2 className="text-xl font-semibold mb-3">Type Variations</h2>
      <div className="space-x-4">
        <Button onClick={() => alert("Primary clicked!")}>
          Primary (default)
        </Button>
        <Button type="secondary" onClick={() => alert("Secondary clicked!")}>
          Secondary
        </Button>
        <Button type="danger" onClick={() => alert("Danger clicked!")}>
          Danger
        </Button>
      </div>
    </div>

    {/* Size Variations */}
    <div>
      <h2 className="text-xl font-semibold mb-3">Size Variations</h2>
      <div className="space-x-4">
        <Button size="sm" onClick={() => alert("Small clicked!")}>
          Small
        </Button>
        <Button size="md" onClick={() => alert("Medium clicked!")}>
          Medium (default)
        </Button>
        <Button size="lg" onClick={() => alert("Large clicked!")}>
          Large
        </Button>
      </div>
    </div>

    {/* Disabled States */}
    <div>
      <h2 className="text-xl font-semibold mb-3">Disabled States</h2>
      <div className="space-x-4">
        <Button disabled>Disabled Primary</Button>
        <Button type="secondary" disabled>
          Disabled Secondary
        </Button>
        <Button type="danger" disabled>
          Disabled Danger
        </Button>
      </div>
    </div>

    {/* Custom Class and Accessibility */}
    <div>
      <h2 className="text-xl font-semibold mb-3">
        Customization & Accessibility
      </h2>
      <div className="space-x-4">
        <Button
          className="uppercase tracking-widest"
          onClick={() => alert("Custom clicked!")}
        >
          Custom Class
        </Button>
        <Button
          aria-label="Accessible Button Description"
          onClick={() => alert("Aria button clicked!")}
        >
          With aria-label
        </Button>
      </div>
    </div>

    {/* New Section: Width Variations */}
    <div>
      <h2 className="text-xl font-semibold mb-3">Width Variations</h2>
      <div className="space-y-4">
        {/* Full Width Button */}
        <div>
          <Button width="full" onClick={() => alert("Full width clicked!")}>
            Full Width ("full")
          </Button>
        </div>

        {/* Auto Width (Default Behavior) */}
        <div className="flex space-x-4 items-start">
          {" "}
          {/* Parent for side-by-side */}
          <Button width="auto" onClick={() => alert("Auto width clicked!")}>
            Auto Width ("auto")
          </Button>
          <span className="text-sm text-gray-600 pt-2">
            {" "}
            (Content-based width)
          </span>
        </div>

        {/* Half and Auto side-by-side for comparison */}
        <div className="border p-4 rounded-md bg-gray-100">
          <p className="text-sm text-gray-700 mb-2">
            Demonstrating fractional widths within a container:
          </p>
          <div className="flex space-x-4 mb-2">
            <Button width="half" onClick={() => alert("Half width clicked!")}>
              Half Width ("half")
            </Button>
            <Button
              width="half"
              type="secondary"
              onClick={() => alert("Another Half width clicked!")}
            >
              Another Half ("half")
            </Button>
          </div>
          <div className="flex space-x-4 mb-2">
            <Button
              width="one-third"
              onClick={() => alert("1/3 width clicked!")}
            >
              One Third ("one-third")
            </Button>
            <Button
              width="two-thirds"
              type="secondary"
              onClick={() => alert("2/3 width clicked!")}
            >
              Two Thirds ("two-thirds")
            </Button>
          </div>
          <div className="flex space-x-4">
            <Button
              width="one-fourth"
              onClick={() => alert("1/4 width clicked!")}
            >
              One Fourth ("one-fourth")
            </Button>
            <Button
              width="three-fourths"
              type="secondary"
              onClick={() => alert("3/4 width clicked!")}
            >
              Three Fourths ("three-fourths")
            </Button>
          </div>
        </div>

        {/* Individual fractional examples if needed */}
        <div className="flex space-x-4 items-start">
          <Button
            width="one-third"
            onClick={() => alert("Standalone 1/3 width clicked!")}
          >
            Standalone One Third
          </Button>
        </div>
      </div>
    </div>
  </div>
);

export default ButtonDemo;
