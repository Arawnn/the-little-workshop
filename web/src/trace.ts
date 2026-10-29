export const robotStates = [
    'idle',
    'moving',
    'inspecting',
    'repairing'
] as const;

export type RobotState = (typeof robotStates)[number];

export function isRobotState(value: string): value is RobotState {
    return robotStates.includes(value as RobotState)
}

export type EventType = "machine.broke" | "action.completed";
export type Outcome = "transition" | "reject" | "ignored";
export type TraceEntry = {
    before: RobotState,
    after: RobotState,
    event: EventType,
    outcome: Outcome,
    reason: string | null,
    t: number
}
 