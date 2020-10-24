/// <reference types="node" />
import { BasicWritableCommand } from '../CommandBase';
export interface DataTransferDownloadRequestProps {
    transferId: number;
    transferStoreId: number;
    transferIndex: number;
}
export declare class DataTransferDownloadRequestCommand extends BasicWritableCommand<DataTransferDownloadRequestProps> {
    static readonly rawName = "FTSU";
    serialize(): Buffer;
}
