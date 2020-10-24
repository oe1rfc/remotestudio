/// <reference types="node" />
import { DeserializedCommand } from '../CommandBase';
export interface DataTransferErrorProps {
    transferId: number;
    errorCode: number;
}
export declare class DataTransferErrorCommand extends DeserializedCommand<DataTransferErrorProps> {
    static readonly rawName = "FTDE";
    static deserialize(rawCommand: Buffer): DataTransferErrorCommand;
    applyToState(): string[];
}
