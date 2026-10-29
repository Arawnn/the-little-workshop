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
