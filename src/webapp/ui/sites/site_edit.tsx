import React from "react";
import {
  Box,
  Button,
  Checkbox,
  FormControl,
  FormHelperText,
  FormLabel,
  Heading,
  Input,
  Stack,
} from "@chakra-ui/react";
import { Site } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { useConfig } from "../../config";
import { useAuth } from "../login/hooks";
import { ApiErrorUI } from "../layout/error_api";
import { Navigate, useSearchParams } from "react-router-dom";
import { Loader } from "../layout/loader";
import { SiteDeletePopoverForm } from "./site_delete";
import { SiteBreadcrumb } from "../layout/breadcrumb";

export const SiteEdit: React.FunctionComponent<{}> = () => {
  let auth = useAuth();
  const config = useConfig();
  const token = auth.authenticatedUser?.token || "";
  const [editSucceed, setEditSucceed] = React.useState<boolean>(false);
  const [error, setError] = React.useState<ApiError>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [site, setSite] = React.useState<Site | null>(null);
  const [params, setParams] = useSearchParams();
  const hostname = params.get("hostname") || "";

  React.useEffect(() => {
    async function loadSite() {
      if (!hostname) {
        return;
      }
      const site = await config.api.site.showSite(token, hostname);
      // console.log(site);
      site
        .map((sit: Site) => setSite(sit))
        .mapErr((err: ApiError) => setError(err));
      // console.log("setIsLoading");
      setIsLoading(false);
    }
    if (hostname) {
      loadSite();
    }
    return () => {
      setSite(null);
      setError(null);
      setIsLoading(true);
    };
  }, [hostname]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const site = {
      hostname: formData.get("hostname") as string,
      root_page_path: formData.get("root_page_path") as string,
      default: formData.get("default") == "true",
      secure: formData.get("secure") == "true",
    };
    const siteResult = await config.api.site.updateSite(
      auth.authenticatedUser?.token || "",
      hostname,
      site
    );

    siteResult
      .map(async (res: boolean) => {
        setEditSucceed(true);
      })
      .mapErr((apiError) => {
        setError(apiError);
      });
  }

  if (editSucceed) {
    return <Navigate to="/admin/sites" replace />;
  }
  if (isLoading) {
    return <Loader label="loading site..." />;
  }

  return (
    site && (
      <Box maxW="720px">
        <SiteBreadcrumb site={site} />
        <Heading>Edit Site</Heading>
        {/* {<SiteBreadcrumb title="new page" />} */}
        <ApiErrorUI error={error} />
        <form onSubmit={handleSubmit}>
          <FormControl>
            <FormLabel>Hostname</FormLabel>
            <Input
              type="text"
              name="hostname"
              placeholder="hostname"
              defaultValue={site.hostname}
            />
            <FormHelperText>Hostname for this site.</FormHelperText>
          </FormControl>
          <FormControl>
            <FormLabel>Root Page</FormLabel>
            <Input
              type="text"
              name="root_page_path"
              placeholder="/index"
              defaultValue={site.root_page_path}
            />
            <FormHelperText>
              Path of the page, that will be the index page for this site (paged
              used for /).
            </FormHelperText>
          </FormControl>
          <FormControl>
            <Checkbox name="default" value="true" defaultChecked={site.default}>
              Default
            </Checkbox>
            <FormHelperText>
              If no site match, fallback to this one.
            </FormHelperText>
          </FormControl>
          <FormControl>
            <Checkbox name="secure" value="true" defaultChecked={site.secure}>
              Secure
            </Checkbox>
            <FormHelperText>Use https.</FormHelperText>
          </FormControl>
          <FormControl>
            <Stack p={4} spacing={4} direction="row" align="right">
              <Button type="submit" colorScheme="teal">
                Submit
              </Button>
              <SiteDeletePopoverForm curSite={site} />
            </Stack>
          </FormControl>
        </form>
      </Box>
    )
  );
};
