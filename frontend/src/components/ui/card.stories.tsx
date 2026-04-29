import type { Meta, StoryObj } from "@storybook/react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "./card";

const meta: Meta<typeof Card> = {
  title: "UI/Card",
  component: Card,
  parameters: {
    layout: "centered",
    docs: {
      description: {
        component:
          "A flexible card component with header, content, and footer sections.",
      },
    },
  },
  tags: ["autodocs"],
  argTypes: {
    className: {
      control: { type: "text" },
      description: "Additional CSS classes",
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Card Title</CardTitle>
        <CardDescription>Card Description</CardDescription>
      </CardHeader>
      <CardContent>
        <p>
          Card Content goes here. This is where you can put your main content.
        </p>
      </CardContent>
      <CardFooter>
        <p>Card Footer</p>
      </CardFooter>
    </Card>
  ),
};

export const WithoutHeader: Story = {
  render: () => (
    <Card className="w-[350px]">
      <CardContent className="pt-6">
        <h3 className="text-lg font-semibold mb-2">Simple Card</h3>
        <p>Card content without header section.</p>
      </CardContent>
    </Card>
  ),
};

export const WithoutFooter: Story = {
  render: () => (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Card Title</CardTitle>
        <CardDescription>Card Description</CardDescription>
      </CardHeader>
      <CardContent>
        <p>Card content without footer section.</p>
      </CardContent>
    </Card>
  ),
};

export const Minimal: Story = {
  render: () => (
    <Card className="w-[350px]">
      <CardContent className="pt-6">
        <p>Minimal card with just content.</p>
      </CardContent>
    </Card>
  ),
};

export const WithActions: Story = {
  render: () => (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Card with Actions</CardTitle>
        <CardDescription>
          This card has action buttons in the footer.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p>Card content with actionable elements.</p>
      </CardContent>
      <CardFooter className="flex justify-between">
        <button className="px-4 py-2 text-sm border rounded-md">Cancel</button>
        <button className="px-4 py-2 text-sm bg-primary text-primary-foreground rounded-md">
          Save
        </button>
      </CardFooter>
    </Card>
  ),
};

export const CustomStyling: Story = {
  render: () => (
    <Card className="w-[350px] border-2 border-primary shadow-lg">
      <CardHeader className="bg-primary text-primary-foreground">
        <CardTitle className="text-white">Custom Styled Card</CardTitle>
        <CardDescription className="text-primary-foreground/80">
          With custom styling
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <p>This card has custom styling applied.</p>
      </CardContent>
    </Card>
  ),
};
