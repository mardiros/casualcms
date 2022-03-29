import React from "react";
import { Box, Heading, Form, Button, Container } from "react-bulma-components";
const { Control, Field, Label, Input } = Form;

function Login() {
  return (
    <Box>
      <Heading>
        Sign In
      </Heading>
      <form method="POST">
        <Field>
          <Label>
            Username:
            <Control>
              <Input name="username" placeholder="username" />
            </Control>
          </Label>
        </Field>
        <Field>
          <Label>
            Password:
            <Control>
              <Input name="password" placeholder="password" type="password" />
            </Control>
          </Label>
        </Field>
        <Button
          type="button"
          color="primary"
        >
          Sign In
        </Button>
      </form >
    </Box >
  );
};


export { Login };
