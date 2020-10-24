/// <reference types="node" />
import { DeserializedCommand } from '../../CommandBase';
import { AtemState } from '../../../state';
import { UpstreamKeyerFlyKeyframe } from '../../../state/video/upstreamKeyers';
export declare class MixEffectKeyFlyKeyframeGetCommand extends DeserializedCommand<UpstreamKeyerFlyKeyframe> {
    static readonly rawName = "KKFP";
    readonly mixEffect: number;
    readonly upstreamKeyerId: number;
    readonly keyFrameId: number;
    constructor(mixEffect: number, upstreamKeyerId: number, keyFrameId: number, properties: UpstreamKeyerFlyKeyframe);
    static deserialize(rawCommand: Buffer): MixEffectKeyFlyKeyframeGetCommand;
    applyToState(state: AtemState): string;
}
