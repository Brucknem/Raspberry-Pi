import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { CameraUrlService } from './camera-url.service';
import { MessagesService } from './messages.service';
import { join } from '../camera-url';
import { catchError, tap } from 'rxjs/operators';
import { CameraControlResult } from './camera-control-result';

@Injectable({
  providedIn: 'root',
})
export class CameraControlService {
  constructor(
    private httpService: HttpClient,
    private cameraUrlService: CameraUrlService,
    private messagesService: MessagesService
  ) {}

  private handleError<T>(
    operation = 'operation',
    result?: T
  ): (error: any) => Observable<T> {
    return (error: any): Observable<T> => {
      this.messagesService.add(`${operation} failed: ${error.message}`);

      // Let the app keep running by returning an empty result.
      return of(result as T);
    };
  }

  private performPostCall(
    operation: string,
    subpath: string,
    password: string
  ): Observable<CameraControlResult> {
    this.messagesService.add(operation + ' requested');
    return this.httpService
      .post<CameraControlResult>(
        join(this.cameraUrlService.streamLocation, subpath),
        JSON.stringify({ password }),
        {
          headers: {
            'Content-Type': 'application/json; charset=utf-8',
          },
        }
      )
      .pipe(
        tap((result: CameraControlResult) =>
          this.messagesService.add(operation + ' succeeded', result.success)
        ),
        catchError(this.handleError<CameraControlResult>(operation))
      );
  }

  startRecording(password: string): Observable<CameraControlResult> {
    return this.performPostCall('Start recording', 'start_recording', password);
  }

  stopRecording(password: string): Observable<CameraControlResult> {
    return this.performPostCall('Stop recording', 'stop_recording', password);
  }
}