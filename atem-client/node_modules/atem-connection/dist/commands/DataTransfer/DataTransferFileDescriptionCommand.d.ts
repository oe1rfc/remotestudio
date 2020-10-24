/// <reference types="node" />
import { BasicWritableCommand } from '../CommandBase';
export interface DataTransferFileDescriptionProps {
    transferId: number;
    name?: string;
    description?: string;
    fileHash: string;
}
export declare class DataTransferFileDescriptionCommand extends BasicWritableCommand<DataTransferFileDescriptionProps> {
    static readonly rawName = "FTFD";
    serialize(): Buffer;
}
