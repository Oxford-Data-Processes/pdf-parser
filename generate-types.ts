import { compile } from 'json-schema-to-typescript';
import * as fs from 'fs';

const schemas = [
  "client_schema.json",
  "financialanalysis_schema.json",
  "assessment_schema.json",
  "document_schema.json",
  "documentmetadata_schema.json",
  "subscription_schema.json",
  "user_schema.json",
];

async function generateTypes() {
  try {
    // Create types directory if it doesn't exist
    if (!fs.existsSync('./types')) {
      fs.mkdirSync('./types');
    }

    // Iterate over schemas
    for (const schemaFile of schemas) {
      // Read the schema
      const schema = JSON.parse(fs.readFileSync(`./json_schemas/${schemaFile}`, 'utf-8'));
      
      // Compile schema to TypeScript
      const ts = await compile(schema, schemaFile.replace('.json', '').replace('_', ' ').replace('schema', '')); // Generate name from file name
      
      // Write the generated TypeScript interface to a file
      fs.writeFileSync(`./typescript/${schemaFile.replace('.json', '.ts').replace('_', '-')}`, ts);
      console.log(`Successfully generated TypeScript interface for ${schemaFile}!`);
    }
  } catch (error) {
    console.error('Error generating TypeScript interface:', error);
  }
}

generateTypes(); 