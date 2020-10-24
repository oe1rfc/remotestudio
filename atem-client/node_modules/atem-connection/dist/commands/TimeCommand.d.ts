/// <reference types="node" />
import { AtemState } from '../state';
import { TimeInfo } from '../state/info';
import * as Enums from '../enums';
import { BasicWritableCommand } from '.';
import { SymmetricalCommand } from './CommandBase';
export declare class TimeCommand extends SymmetricalCommand<TimeInfo> {
    static readonly rawName = "Time";
    constructor(properties: TimeInfo | Omit<TimeInfo, 'dropFrame'>);
    serialize(): Buffer;
    static deserialize(rawCommand: Buffer): TimeCommand;
    applyToState(state: AtemState): string;
}
export declare class TimeRequestCommand extends BasicWritableCommand<null> {
    static readonly rawName = "TiRq";
    static readonly minimumVersion = Enums.ProtocolVersion.V8_0;
    constructor();
    serialize(): Buffer;
}
