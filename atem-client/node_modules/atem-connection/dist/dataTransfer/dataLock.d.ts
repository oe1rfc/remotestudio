import { Commands } from '..';
import DataTransfer from './dataTransfer';
export default class DataLock {
    private storeId;
    private isLocked;
    private taskQueue;
    activeTransfer: DataTransfer | undefined;
    private queueCommand;
    constructor(storeId: number, queueCommand: (cmd: Commands.ISerializableCommand) => void);
    enqueue(transfer: DataTransfer): Promise<DataTransfer>;
    private dequeueAndRun;
    lockObtained(): void;
    lostLock(): void;
    updateLock(locked: boolean): void;
    transferFinished(): void;
    transferErrored(code: number): void;
}
