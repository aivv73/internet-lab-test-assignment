import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';

import { ContactApiService } from './contact-api.service';
import { ApiErrorResponse, ContactRequest, ContactResponse } from './contact.models';

type SubmissionState = 'idle' | 'submitting' | 'success' | 'error';

type ContactForm = FormGroup<{
  name: FormControl<string>;
  email: FormControl<string>;
  phone: FormControl<string>;
  comment: FormControl<string>;
}>;

@Component({
  selector: 'app-root',
  imports: [ReactiveFormsModule],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  private readonly contactApi = inject(ContactApiService);

  protected readonly state = signal<SubmissionState>('idle');
  protected readonly response = signal<ContactResponse | null>(null);
  protected readonly apiError = signal<string | null>(null);

  protected readonly form: ContactForm = new FormGroup({
    name: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required, Validators.minLength(2), Validators.maxLength(100)],
    }),
    email: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required, Validators.email],
    }),
    phone: new FormControl('', {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.minLength(7),
        Validators.maxLength(32),
        Validators.pattern(/^[0-9+\s().-]+$/),
      ],
    }),
    comment: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required, Validators.minLength(10), Validators.maxLength(2000)],
    }),
  });

  protected readonly isSubmitting = computed(() => this.state() === 'submitting');

  protected submit(): void {
    this.form.markAllAsTouched();
    this.apiError.set(null);
    this.response.set(null);

    if (this.form.invalid || this.isSubmitting()) {
      return;
    }

    this.state.set('submitting');
    this.contactApi
      .submitContact(this.form.getRawValue() satisfies ContactRequest)
      .pipe(finalize(() => this.state.update((state) => (state === 'submitting' ? 'idle' : state))))
      .subscribe({
        next: (response) => {
          this.response.set(response);
          this.state.set('success');
          this.form.reset();
        },
        error: (error: HttpErrorResponse) => {
          this.apiError.set(formatApiError(error));
          this.state.set('error');
        },
      });
  }

  protected fieldError(field: keyof ContactForm['controls']): string | null {
    const control = this.form.controls[field];
    if (!control.touched || control.valid) {
      return null;
    }

    if (control.hasError('required')) {
      return 'This field is required.';
    }

    if (control.hasError('email')) {
      return 'Use a valid email address.';
    }

    if (control.hasError('minlength')) {
      return field === 'comment' ? 'Write at least 10 characters.' : 'Use at least 2 characters.';
    }

    if (control.hasError('maxlength')) {
      return 'This value is too long.';
    }

    if (control.hasError('pattern')) {
      return 'Use digits, spaces, +, -, dots or parentheses.';
    }

    return 'Check this value.';
  }
}

function formatApiError(error: HttpErrorResponse): string {
  const payload = error.error as ApiErrorResponse | null;

  if (error.status === 429) {
    const retryAfter = payload?.error?.details?.['retry_after_seconds'];
    return typeof retryAfter === 'number'
      ? `Rate limit reached. Try again in ${retryAfter} seconds.`
      : 'Rate limit reached. Please try again later.';
  }

  if (error.status === 422) {
    return 'Validation failed on the API. Check the fields and try again.';
  }

  if (payload?.error?.message) {
    return payload.error.message;
  }

  if (error.status === 0) {
    return 'Cannot reach the API. Start FastAPI or use the Railway deployment.';
  }

  return 'The API could not process the request. Please try again.';
}
