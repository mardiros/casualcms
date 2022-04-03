import { Heading } from "react-bulma-components";
import * as React from "react";

export const PageNotFound: React.FunctionComponent<{}> = () => {
  return (
    <>
      <Heading>Page Not Found</Heading>
      <Heading subtitle>This is probably not a problem with npm.</Heading>
    </>
  );
};
