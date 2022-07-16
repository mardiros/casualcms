import { Box, Heading } from "@chakra-ui/react";
import * as React from "react";
import { ApiError } from "../../casualcms/domain/ports";

type ApiErrorUIProps = {
  error: ApiError;
};

export const ApiErrorUI: React.FunctionComponent<ApiErrorUIProps> = (
  props: ApiErrorUIProps
) => {
  const error = props.error;
  return (
    <Box>
      {error && (
        <>
          <Heading>Errors encountered</Heading>
          <ul>
            {error &&
              [...error.keys()].map((k) => <li key={k}> {error.get(k)} </li>)}
          </ul>
        </>
      )}
    </Box>
  );
};
