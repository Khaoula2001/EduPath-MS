declare module 'rxjs' {
    export interface Observer<T> {
        next: (value: T) => void;
        error: (err: any) => void;
        complete: () => void;
    }

    export class Subscription {
        unsubscribe(): void;
        add(teardown: any): void;
    }

    export class Observable<T> {
        constructor(subscribe?: (subscriber: any) => void);
        subscribe(observer?: Partial<Observer<T>>): Subscription;
        subscribe(
            next?: (value: T) => void,
            error?: (error: any) => void,
            complete?: () => void
        ): Subscription;
        pipe(...operations: any[]): Observable<any>;
        toPromise(): Promise<T>;
    }

    export class Subject<T> extends Observable<T> {
        next(value: T): void;
        error(err: any): void;
        complete(): void;
        asObservable(): Observable<T>;
    }

    export class BehaviorSubject<T> extends Subject<T> {
        constructor(value: T);
        value: T;
        getValue(): T;
    }

    export class ReplaySubject<T> extends Subject<T> {
        constructor(bufferSize?: number, windowTime?: number);
    }

    export function of<T>(...args: T[]): Observable<T>;
    export function forkJoin(...args: any[]): Observable<any>;
    export function fromEvent(...args: any[]): Observable<any>;
    export function timer(dueTime: number | Date, periodOrScheduler?: any): Observable<number>;
    export function interval(period: number): Observable<number>;
    export function throwError(error: any): Observable<never>;
}

declare module 'rxjs/operators' {
    export function map<T, R>(project: (value: T, index: number) => R): any;
    export function catchError<T, R>(selector: (err: any, caught: any) => any): any;
    export function switchMap<T, R>(project: (value: T, index: number) => any): any;
    export function tap<T>(observerOrNext?: any): any;
    export function filter<T>(predicate: (value: T, index: number) => boolean): any;
    export function take<T>(count: number): any;
    export function takeUntil<T>(notifier: any): any;
    export function debounceTime<T>(dueTime: number): any;
    export function distinctUntilChanged<T>(compare?: (x: T, y: T) => boolean): any;
    export function finalize<T>(callback: () => void): any;
}
