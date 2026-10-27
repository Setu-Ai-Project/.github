// Represents user mode: learner asking doubts, or mentor assisting learners.
export type Mode = "learner" | "mentor";

// Lifecycle status of a doubt.
export type DoubtStatus = "open" | "answered";

// Information about a mentor's answer to a doubt.
export interface MentorReply {
  mentorName: string;
  text: string;
  // ISO 8601 formatted date-time string when the reply was submitted.
  repliedAt: string;
}

// A doubt submitted by a learner.
// The `reply` property is optional: undefined while the doubt is "open",
// and populated when a mentor answers and changes status to "answered".
export interface Doubt {
  id: string;
  learnerName: string;
  question: string;
  status: DoubtStatus;
  // ISO 8601 formatted date-time string when the doubt was asked.
  createdAt: string;
  reply?: MentorReply;
}
