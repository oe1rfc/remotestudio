/// <reference types="node" />
import { BasicWritableCommand } from '../CommandBase';
import { Enums } from '../..';
export interface DataTransferUploadRequestProps {
    transferId: number;
    transferStoreId: number;
    transferIndex: number;
    size: number;
    mode: Enums.TransferMode;
}
export declare class DataTransferUploadRequestCommand extends BasicWritableCommand<DataTransferUploadRequestProps> {
    static readonly rawName = "FTSD";
    serialize(): Buffer;
}
