import { Commands, Enums } from '..';
export default abstract class DataTransfer {
    state: Enums.TransferState;
    readonly _transferId: number;
    readonly storeId: number;
    private readonly completionPromise;
    resolvePromise: (value?: DataTransfer | PromiseLike<DataTransfer> | undefined) => void;
    rejectPromise: (reason?: any) => void;
    constructor(transferId: number, storeId: number);
    readonly transferId: number;
    readonly promise: Promise<DataTransfer>;
    abstract start(): Commands.ISerializableCommand[];
    abstract handleCommand(command: Commands.IDeserializedCommand): Commands.ISerializableCommand[];
    abstract gotLock(): Commands.ISerializableCommand[];
}
