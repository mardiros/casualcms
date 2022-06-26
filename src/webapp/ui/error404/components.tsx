import { Heading, Text } from '@chakra-ui/react'
import * as React from "react";

export const PageNotFound: React.FunctionComponent<{}> = () => {
  return (
    <>
      <Heading>
        Page Not Found
      </Heading>
      <Text>
        This is probably not a problem with npm.
      </Text>
    </>
  );
};
