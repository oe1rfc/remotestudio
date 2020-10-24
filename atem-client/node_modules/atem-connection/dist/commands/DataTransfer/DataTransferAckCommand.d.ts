/// <reference types="node" />
import { DeserializedCommand } from '../CommandBase';
export interface DataTransferAckProps {
    transferId: number;
    transferIndex: number;
}
export declare class DataTransferAckCommand extends DeserializedCommand<DataTransferAckProps> {
    static readonly rawName = "FTUA";
    static deserialize(rawCommand: Buffer): DataTransferAckCommand;
    applyToState(): string[];
}
