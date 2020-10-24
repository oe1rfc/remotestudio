/// <reference types="node" />
import { AtemState } from '../state';
import { ProtocolVersion } from '../enums';
export interface IDeserializedCommand {
    properties: any;
    applyToState(state: AtemState): string | string[];
}
export declare abstract class DeserializedCommand<T> implements IDeserializedCommand {
    static readonly rawName?: string;
    static readonly minimumVersion?: ProtocolVersion;
    readonly properties: Readonly<T>;
    constructor(properties: T);
    abstract applyToState(state: AtemState): string | string[];
}
export interface ISerializableCommand {
    serialize(version: ProtocolVersion): Buffer;
}
export declare abstract class BasicWritableCommand<T> implements ISerializableCommand {
    static readonly rawName?: string;
    static readonly minimumVersion?: ProtocolVersion;
    protected _properties: T;
    readonly properties: Readonly<T>;
    constructor(properties: T);
    abstract serialize(version: ProtocolVersion): Buffer;
}
export declare abstract class WritableCommand<T> extends BasicWritableCommand<Partial<T>> {
    static readonly MaskFlags?: {
        [key: string]: number;
    };
    flag: number;
    constructor();
    updateProps(newProps: Partial<T>): boolean;
    protected _updateProps(newProps: {
        [key: string]: any;
    }): boolean;
}
export declare abstract class SymmetricalCommand<T> extends DeserializedCommand<T> implements ISerializableCommand {
    abstract serialize(version: ProtocolVersion): Buffer;
}
