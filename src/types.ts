export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]


export interface Address {
  address_line_1: string
  address_line_2?: string
  city: string
  postcode: string
  country_name: string
  country_code: string
}

export enum PaymentMethodType {
  CreditCard = "credit_card",
  DebitCard = "debit_card",
  PayPal = "paypal",
  BankTransfer = "bank_transfer",
}

export interface PaymentMethod {
  type: PaymentMethodType;
  last_four: string;
  card_brand: string;
  expiration_date: string;
  is_default: boolean;
  billing_address?: Address;
}


export interface Database {
  public: {
    tables: {
      users: {
        Row: {
          id: string
          email: string
          first_name: string 
          last_name: string
          avatar_url: string | null
          address: Address
          payment_method: PaymentMethod | null
          subscription_tier: string | null
          subscription_status: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id: string
          email: string
          full_name?: string | null
          avatar_url?: string | null
          billing_address?: Json | null
          payment_method?: Json | null
          subscription_tier?: string | null
          subscription_status?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          email?: string
          full_name?: string | null
          avatar_url?: string | null
          billing_address?: Json | null
          payment_method?: Json | null
          subscription_tier?: string | null
          subscription_status?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      clients: {
        Row: {
          id: string
          created_by: string
          first_name: string
          last_name: string
          email: string
          phone_number: string
          date_of_birth: string
          address: Json
          employment_status: string
          annual_income: number
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          created_by: string
          first_name: string
          last_name: string
          email: string
          phone_number: string
          date_of_birth: string
          address: Json
          employment_status: string
          annual_income: number
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          created_by?: string
          first_name?: string
          last_name?: string
          email?: string
          phone_number?: string
          date_of_birth?: string
          address?: Json
          employment_status?: string
          annual_income?: number
          created_at?: string
          updated_at?: string
        }
      }
      co_applicants: {
        Row: {
          id: string
          client_id: string
          first_name: string
          last_name: string
          email: string
          phone_number: string
          date_of_birth: string
          address: Json
          relationship: string
          employment_status: string
          annual_income: number
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          client_id: string
          first_name: string
          last_name: string
          email: string
          phone_number: string
          date_of_birth: string
          address: Json
          relationship: string
          employment_status: string
          annual_income: number
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          client_id?: string
          first_name?: string
          last_name?: string
          email?: string
          phone_number?: string
          date_of_birth?: string
          address?: Json
          relationship?: string
          employment_status?: string
          annual_income?: number
          created_at?: string
          updated_at?: string
        }
      }
      subscriptions: {
        Row: {
          id: string
          user_id: string
          stripe_customer_id: string | null
          stripe_subscription_id: string | null
          plan_id: string
          status: string
          current_period_start: string | null
          current_period_end: string | null
          cancel_at: string | null
          canceled_at: string | null
          trial_start: string | null
          trial_end: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          stripe_customer_id?: string | null
          stripe_subscription_id?: string | null
          plan_id: string
          status: string
          current_period_start?: string | null
          current_period_end?: string | null
          cancel_at?: string | null
          canceled_at?: string | null
          trial_start?: string | null
          trial_end?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          stripe_customer_id?: string | null
          stripe_subscription_id?: string | null
          plan_id?: string
          status?: string
          current_period_start?: string | null
          current_period_end?: string | null
          cancel_at?: string | null
          canceled_at?: string | null
          trial_start?: string | null
          trial_end?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      documents: {
        Row: {
          id: string
          client_id: string
          name: string
          type: string
          status: string
          file_path: string
          file_size: number
          mime_type: string
          validation_errors: string[]
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          client_id: string
          name: string
          type: string
          status: string
          file_path: string
          file_size: number
          mime_type: string
          validation_errors?: string[]
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          client_id?: string
          name?: string
          type?: string
          status?: string
          file_path?: string
          file_size?: number
          mime_type?: string
          validation_errors?: string[]
          created_at?: string
          updated_at?: string
        }
      }
      document_metadata: {
        Row: {
          id: string
          document_id: string
          metadata: {
            bank_name: string | null
            account_type: string | null
            statement_period: string | null
            sort_code: string | null
            account_number: string | null
            account_holder: string | null
            total_money_in: number | null
            total_money_out: number | null
            start_balance: number | null
            end_balance: number | null
          }
          analysis_results: Json | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          document_id: string
          metadata: {
            bank_name: string | null
            account_type: string | null
            statement_period: string | null
            sort_code: string | null
            account_number: string | null
            account_holder: string | null
            total_money_in: number | null
            total_money_out: number | null
            start_balance: number | null
            end_balance: number | null
          }
          analysis_results?: Json | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          document_id?: string
          metadata: {
            bank_name: string | null
            account_type: string | null
            statement_period: string | null
            sort_code: string | null
            account_number: string | null
            account_holder: string | null
            total_money_in: number | null
            total_money_out: number | null
            start_balance: number | null
            end_balance: number | null
          }
          analysis_results?: Json | null
          created_at?: string
          updated_at?: string
        }
      }
      config: {
        Row: {
          id: string
          used_spots: number
          created_at: string
          updated_at: string
        }
        Insert: {
          id: string
          used_spots?: number
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          used_spots?: number
          created_at?: string
          updated_at?: string
        }
      }
      financial_analysis: {
        Row: {
          id: string
          client_id: string
          analysis_date: string
          income_analysis: Json
          expense_analysis: Json
          risk_assessment: Json
        }
        Insert: {
          id?: string
          client_id: string
          analysis_date?: string
          income_analysis: Json
          expense_analysis: Json
          risk_assessment: Json
        }
        Update: {
          id?: string
          client_id?: string
          analysis_date?: string
          income_analysis?: Json
          expense_analysis?: Json
          risk_assessment?: Json
        }
      }
      assessments: {
        Row: {
          id: string
          client_id: string
          created_at: string
          assessment_data: Json
          analysis_period: Json
        }
        Insert: {
          id?: string
          client_id: string
          created_at?: string
          assessment_data: Json
          analysis_period: Json
        }
        Update: {
          id?: string
          client_id?: string
          created_at?: string
          assessment_data?: Json
          analysis_period?: Json
        }
      }
      transactions: {
        Row: {
          id: string
          client_id: string
          period: Json
          accounts: Json[]
          categorized_transactions: Json
          summary: Json
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          client_id: string
          period: Json
          accounts?: Json[]
          categorized_transactions: Json
          summary: Json
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          client_id?: string
          period?: Json
          accounts?: Json[]
          categorized_transactions?: Json
          summary?: Json
          created_at?: string
          updated_at?: string
        }
      }
    }
    Views: {}
    Functions: {
      delete_user: {
        Args: Record<string, never>
        Returns: boolean
      }
    }
  }
} 